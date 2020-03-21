% Read the MAT data after processing with exp info.
% E:\BaiduNetdiskDownload
% 191172_in_context.mat

% <in_context_columns> store column information about <in_context_msblocks>.
% The last column is <ms_ts> used to match with behavior timestamps.
%
% <in_context_behavetrial_columns> store column information about
% <in_context_behavetrialblocks> and <in_context_behaveblocks>. 
% for each trial, there are 24 columns.

% {'ms_ts','be_frame','index','be_ts',
%     'Head_x','Head_y','Head_lh','Body_x','Body_y','Body_lh',
%     'Tail_x','Tail_y','Tail_lh','correct_ts','Headspeeds','Headspeed_angles',
%     'Bodyspeeds','Bodyspeed_angles',
%     'Tailspeeds','Tailspeed_angles','headdirections','taildirections','arch_angles',
%     'in_context'}
% ms_ts, be_ts is already matched.  unit is minisecond.
% <be_frame> and <index> is frame number in the behavior video.

% <in_context_behaveblocks> is collection of all the data.
% 12 cells, each cell is one block with some trials.

% <in_context_behavetrialblocks> is further divided into blocks. % blocks - trials - frames x 24 columns.
%  each cell is one  block. 
% for each block,  there are some cells, each cell is one trial
% in each trial, animal is running through the context for one time.
% in each trial, the data is orgnized by 24 columns.

% <in_context_columns> is the index for cells.
% <in_context_msblocks> is the same way organized as <in_context_behaveblocks>.
% <in_context_msblocks>, the last column is the timestamps, it is the same
% as the first column of <in_context_behaveblocks> for  the same order of
% cells.
% <in_context_coords> is the context coordinates. nblocks x 2 cells. 2nd
% cell is for the coordinates. For each video, the camera is rotated
% together with the linear track, therefore, animal's position in the track
% can be simplified as the movement in the X axis.

clc; clear; close all; Startup1;
%% load the data and update MAT file (must RUN once)
filepath= 'D:\miniscope data 2\Linear Track'; % 'E:\BaiduNetdiskDownload';
file1 = fullfile(filepath,'191172_in_context.mat');
animaldata = load( file1); 
blockname={'90A','90B','135B','135A','90B2','90A2','45A','45B','90A3','90B3','90AA','90BB'}; % in the sequential order.

% [90,90,135,135,90,90,45,45,90,90,90,90]
% ['191172A-20191028-202245',
%  '191172B-20191029-105432',
%  '191172B-20191029-145505',
%  '191172A-20191029-150917',
%  '191172B-20191030-131900',
%  '191172A-20191030-133045',
%  '191172A-20191031-123313',
%  '191172B-20191031-124451',
%  '191172A-20191101-193008',
%  '191172B-20191101-194017',
%  '191172A1-20191102-145304',
%  '191172B1-20191102-150201']

behav_col = animaldata.in_context_behavetrial_columns;
behav = animaldata.in_context_behaveblocks;
% cell ID for accepted cells in <in_context_columns>
cellROI = cellfun( @str2num, animaldata.in_context_columns(1, 1:end-1));  % <in_context_columns>, the last column is text
%------------------------------------------------------
% calculate the running direction
coords = animaldata.in_context_coords(:, 2); % coordinates
in_context_behavetrial_columns = animaldata.in_context_behavetrial_columns;
in_context_behavetrial_columns = [in_context_behavetrial_columns, 'runningleft'];
for j = 1 : numel( blockname) % each block    
    behavetrialblocks  = animaldata.in_context_behavetrialblocks{j}; % behavioral data with trials defined
    % calculate based on each trial
    for i = 1 : numel( behavetrialblocks)
        bodyX = behavetrialblocks{i}(:,8); 
        % if early bodyX coordinates < late ones, the running is left to right
        nX = numel( bodyX);
        if mean( bodyX( round( 0.2 * nX) )) < mean( bodyX( end - round( 0.2 * nX)))
            runningleft = false;
        else
            runningleft = true;
        end
        behavetrialblocks{i}(:,25) = runningleft;        
    end   
    animaldata.in_context_behavetrialblocks{j} = behavetrialblocks;
end
%------------------------------------------------------
% Update MAT file.
animaldata.bUpdated   = false; % force to update MAT file
% update the specific information about this animal
if ~isfield( animaldata, 'bUpdated') || ~animaldata.bUpdated    
    bUpdated = true;
    in_context_behavetrialblocks = animaldata.in_context_behavetrialblocks;
    save(file1, 'in_context_behavetrial_columns', 'in_context_behavetrialblocks', '-append' );
    save( file1, 'blockname', 'cellROI', 'bUpdated', '-append');   
end

%% FR calculation for (all trials x included cells ) by each session. Running 1 min. Only needed for trial-based FR analysis
FRall = cell(1, numel( blockname)); % FR for each session
for j = 1 : numel( blockname) % each session    
    behavetrialblocks  = animaldata.in_context_behavetrialblocks{j}; % behavioral data with trials defined
    % in_context_msblocks = animaldata.in_context_msblocks{ j}; % miniscope data    
    in_context_msblocks = animaldata.in_context_msblocksCaEvent{ j}; % miniscope data    
    stampms = in_context_msblocks( :, end);
    FR = nan( numel( behavetrialblocks), numel( cellROI ) );
    % calculate based on each trial
    for i = 1 : numel( behavetrialblocks)
        stamp1 = behavetrialblocks{i}(:,1); % stamps for a given trial
        sig1 = in_context_msblocks( ismember( stamp1, stampms), cellROI); % ms data of included cells in the given trial
        % calculate FR for included cells in the given trial
        FR( i, cellROI) = calcFR( sig1( :, cellROI)',  'type', 'trace event detected');
        % for k = 1 : numel( cellROI);    FR( i, k ) = calcFR( sig1(:, k)',  'type', 'trace event'); end
    end    
    FRall{ j} = [ FRall{ j}; FR]; % FR <trial x cell>
end

%% Find the context specific cells,  putting all trials together

% may be multiple sessions together.
idx = 1 : numel( blockname) - 2; % the last 2 is modified context
sigA = [];
for i = idx( contains(blockname( idx),'A'))
    sig = animaldata.in_context_msblocksCaEvent{ i};
    sigA = [sigA; sig( :, cellROI) ];
end

sigB = [];
for i = idx( contains(blockname( idx),'B'))
    sig = animaldata.in_context_msblocksCaEvent{ i};
    sigB = [sigB; sig( :, cellROI) ];
end

% ranksum test
p=zeros(size(sigA,2),1);
for n=1:size(sigA,2)
    p(n)=ranksum( sigA( :, n), sigB( :, n),'tail','both');
end
idCtxSel=find(p<=0.05);

% calculate firing rate 
FRA = nan( size( sigB, 2), 1);
FRB = nan( size( sigA, 2), 1);
for j = 1 : size(sigA,2)
    FRA( j) = calcFR( sigA( :, j )',  'type', 'whole trace');
    FRB( j) = calcFR( sigB( :, j )',  'type', 'whole trace');    
end
diffAB = FRA - FRB;
% plot some exmaple cells for context selectivity
clear idtemp
[~, idtemp] = sort( diffAB( idCtxSel), 'desc' );

idtemp1 =  idCtxSel( idtemp( 1 : 20));
aa = sigB(:,  idtemp1 );
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
figure; 
subplot( 1, 2, 1)
plot(  cc' );
axis tight
title('B');

hold on
aa = sigA(:,  idtemp1);
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
subplot( 1, 2, 2)
plot(  cc' );
axis tight
title('A');

% plot some example cells
idtemp1 =  idCtxSel( idtemp( 21 : 40));
aa = sigB(:,  idtemp1 );
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
figure; 
subplot( 1, 2, 1)
plot(  cc' );
axis tight
title('B');

hold on
aa = sigA(:,  idtemp1);
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
subplot( 1, 2, 2)
plot(  cc' );
axis tight
title('A');

%% Find the orientation specific cells, based on the context cells (defined by pooled context trials>
clear idx1 idx2 idx3 
idx = 1 : numel( blockname) - 2; % the last 2 is modified context
idx1 = contains(blockname( idx),'90A');
idx2 = contains(blockname( idx),'45A');
idx3 = contains(blockname( idx),'135A');

sigA = [];
for i = idx( contains(blockname( idx),'A'))
    sig = animaldata.in_context_msblocks{ i};
    sigA = [sigA; sig( :, cellROI) ];
end

sigB = [];
for i = idx( contains(blockname( idx),'B'))
    sig = animaldata.in_context_msblocks{ i};
    sigB = [sigB; sig( :, cellROI) ];
end

% ranksum test
p=zeros(size(sigA,2),1);
for n=1:size(sigA,2)
    p(n)=ranksum( sigA( :, n), sigB( :, n),'tail','left');
end
idCtxSel=find(p<=0.05);

% calculate firing rate 
FRA = nan( size( sigB, 2), 1);
FRB = nan( size( sigA, 2), 1);
for j = 1 : size(sigA,2)
    FRA( j) = calcFR( sigA( :, j )',  'type', 'whole trace');
    FRB( j) = calcFR( sigB( :, j )',  'type', 'whole trace');    
end
diffAB = FRA - FRB;

sig90A = [];
for i = idx( idx1)
    sig = animaldata.in_context_msblocks{ i};
    sig90A = [sig90A; sig( :, cellROI) ];
end

sig45A = [];
for i = idx( idx2)
    sig = animaldata.in_context_msblocks{ i};
    sig45A = [sig45A; sig( :, cellROI) ];
end

sig135A = [];
for i = idx( idx3)
    sig = animaldata.in_context_msblocks{ i};
    sig135A = [sig135A; sig( :, cellROI) ];
end

%
% ranksum test
p=zeros(size(sig90A,2),1);
for n=1:size(sig90A,2)
    p(n)=ranksum( sig90A( :, n), sig135A( :, n),'tail','left');
end
idOriSelA=find(p<=0.05);

clear idtemp
[~, idtemp] = sort( diffAB( intersect( idCtxSel, idOriSelA)), 'desc' );
% plot the results.
idtemp2 = intersect( idCtxSel, idOriSelA);
idtemp1 =  idtemp2 ( idtemp( 1 : 20));
aa = sig90A(:,  idtemp1 );
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
figure; 
subplot( 1, 5, 1)
plot(  cc' );
axis tight
title('90A');

hold on
aa = sig135A(:,  idtemp1);
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
subplot( 1, 5, 2)
plot(  cc' );
axis tight
title('135A');

hold on
aa = sig45A(:,  idtemp1);
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
subplot( 1, 5, 3)
plot(  cc' );
axis tight
title('45A');

hold on
aa = sigB(:,  idtemp1);
aa=aa./max(aa,[],1); % normalize by the peak.
cc = aa' + (1 : 20)';
subplot( 1, 5, [4 5])
plot(  cc' );
axis tight
title('B');

%% Find context cells, consider different angles separately
idx = 1 : numel( blockname) - 2; % the last 2 is modified context
idx90A = contains(blockname( idx),'90A'); sig90A = [];
idx45A = contains(blockname( idx),'45A'); sig45A = [];
idx135A = contains(blockname( idx),'135A'); sig135A = [];
idx90B = contains(blockname( idx),'90B'); sig90B = [];
idx45B = contains(blockname( idx),'45B'); sig45B = [];
idx135B = contains(blockname( idx),'135B'); sig135B = [];

% ms = animaldata.in_context_msblocks;
ms = animaldata.in_context_msblocksCaEvent;
for i = idx( idx90A); sig = ms{ i}; sig90A = [sig90A; sig( :, cellROI) ]; end
for i = idx( idx45A); sig = ms{ i}; sig45A = [sig45A; sig( :, cellROI) ]; end
for i = idx( idx135A); sig = ms{ i}; sig135A = [sig135A; sig( :, cellROI) ]; end
for i = idx( idx90B); sig = ms{ i}; sig90B = [sig90B; sig( :, cellROI) ]; end
for i = idx( idx45B); sig = ms{ i}; sig45B = [sig45B; sig( :, cellROI) ]; end
for i = idx( idx135B); sig = ms{ i}; sig135B = [sig135B; sig( :, cellROI) ]; end

sigA = []; for i = idx( contains(blockname( idx),'A')); sig = ms{ i}; sigA = [sigA; sig( :, cellROI) ]; end
sigB = []; for i = idx( contains(blockname( idx),'B')); sig = ms{ i}; sigB = [sigB; sig( :, cellROI) ]; end

cellnum = size(sigA,2);

% ranksum test for A and B with the same angle
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig90A( :, n), sig90B( :, n),'tail','both'); end
idCtxSel90=find(p<=0.05);
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig45A( :, n), sig45B( :, n),'tail','both'); end
idCtxSel45=find(p<=0.05);
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig135A( :, n), sig135B( :, n),'tail','both'); end
idCtxSel135=find(p<=0.05);

clear idCtxSel; idCtxSel = intersect( intersect( idCtxSel90, idCtxSel45), intersect( idCtxSel90, idCtxSel135) ) ;

% plot the results.
clear idtemp; figure;
[~, idtemp] = sort( diffAB( idCtxSel), 'desc' );
idtemp1 =  idCtxSel ( idtemp( 1 : 20));

aa = sig90A(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 1)
plot(  cc' ); axis tight; title('90A'); hold on

aa = sig90B(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 2)
plot(  cc' ); axis tight; title('90B'); hold on

aa = sig45A(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 3)
plot(  cc' ); axis tight; title('45A'); hold on

aa = sig45B(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 4)
plot(  cc' ); axis tight; title('45B'); hold on

aa = sig135A(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 5)
plot(  cc' ); axis tight; title('135A'); hold on

aa = sig135B(:,  idtemp1 );
aa=aa./max(aa,[],1); cc = aa' + (1 : 20)';
subplot( 1, 6, 6)
plot(  cc' ); axis tight; title('135B'); hold on

%% Find context cells, consider different angles separately, trials are pooled
idx = 1 : numel( blockname) - 2; % the last 2 is modified context
idx90A = contains(blockname( idx),'90A'); sig90A = [];
idx45A = contains(blockname( idx),'45A'); sig45A = [];
idx135A = contains(blockname( idx),'135A'); sig135A = [];
idx90B = contains(blockname( idx),'90B'); sig90B = [];
idx45B = contains(blockname( idx),'45B'); sig45B = [];
idx135B = contains(blockname( idx),'135B'); sig135B = [];
% ms = animaldata.in_context_msblocks;
ms = animaldata.in_context_msblocksCaEvent;
for i = idx( idx90A); sig = ms{ i}; sig90A = [sig90A; sig( :, cellROI) ]; end
for i = idx( idx45A); sig = ms{ i}; sig45A = [sig45A; sig( :, cellROI) ]; end
for i = idx( idx135A); sig = ms{ i}; sig135A = [sig135A; sig( :, cellROI) ]; end
for i = idx( idx90B); sig = ms{ i}; sig90B = [sig90B; sig( :, cellROI) ]; end
for i = idx( idx45B); sig = ms{ i}; sig45B = [sig45B; sig( :, cellROI) ]; end
for i = idx( idx135B); sig = ms{ i}; sig135B = [sig135B; sig( :, cellROI) ]; end

sigA = []; for i = idx( contains(blockname( idx),'A')); sig = ms{ i}; sigA = [sigA; sig( :, cellROI) ]; end
sigB = []; for i = idx( contains(blockname( idx),'B')); sig = ms{ i}; sigB = [sigB; sig( :, cellROI) ]; end

cellnum = size(sigA,2);

% ranksum test for A and B with the same angle
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig90A( :, n), sig90B( :, n),'tail','left'); end
idCtxSel90=find(p<=0.05);
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig45A( :, n), sig45B( :, n),'tail','left'); end
idCtxSel45=find(p<=0.05);
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( sig135A( :, n), sig135B( :, n),'tail','left'); end
idCtxSel135=find(p<=0.05);

clear idCtxSel; idCtxSel1 = intersect( intersect( idCtxSel90, idCtxSel45), intersect( idCtxSel90, idCtxSel135) ) ;

%% Find the orientation specific cells, based on the context cells (FR calculated for each trial>, require FR calculation. 
% prepare for the <sig>
idx = 1 : numel( blockname) - 2; % the last 2 is modified context
idx90A = contains(blockname( idx),'90A'); sig90A = [];
idx45A = contains(blockname( idx),'45A'); sig45A = [];
idx135A = contains(blockname( idx),'135A'); sig135A = [];
idx90B = contains(blockname( idx),'90B'); sig90B = [];
idx45B = contains(blockname( idx),'45B'); sig45B = [];
idx135B = contains(blockname( idx),'135B'); sig135B = [];
clear ms
ms = animaldata.in_context_msblocks; 
% ms = animaldata.in_context_msblocksCaEvent;
for i = idx( idx90A); sig = ms{ i}; sig90A = [sig90A; sig( :, cellROI) ]; end
for i = idx( idx45A); sig = ms{ i}; sig45A = [sig45A; sig( :, cellROI) ]; end
for i = idx( idx135A); sig = ms{ i}; sig135A = [sig135A; sig( :, cellROI) ]; end
for i = idx( idx90B); sig = ms{ i}; sig90B = [sig90B; sig( :, cellROI) ]; end
for i = idx( idx45B); sig = ms{ i}; sig45B = [sig45B; sig( :, cellROI) ]; end
for i = idx( idx135B); sig = ms{ i}; sig135B = [sig135B; sig( :, cellROI) ]; end

sigA = []; for i = idx( contains(blockname( idx),'A')); sig = ms{ i}; sigA = [sigA; sig( :, cellROI) ]; end
sigB = []; for i = idx( contains(blockname( idx),'B')); sig = ms{ i}; sigB = [sigB; sig( :, cellROI) ]; end

% ranksum test for A and B with the same angle
cellnum = size(sigA,2);

FR90Acell = FRall ( idx90A); FR90A=[]; for i = 1 : numel( FR90Acell); FR90A = [FR90A; FR90Acell{i}]; end
FR90Bcell = FRall ( idx90B); FR90B=[]; for i = 1 : numel( FR90Bcell); FR90B = [FR90B; FR90Bcell{i}]; end
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( FR90A( :, n), FR90B( :, n),'tail','both'); end
idCtxSel90=find(p<=0.05);

FR45Acell = FRall ( idx45A); FR45A=[]; for i = 1 : numel( FR45Acell); FR45A = [FR45A; FR45Acell{i}]; end
FR45Bcell = FRall ( idx45B); FR45B=[]; for i = 1 : numel( FR45Bcell); FR45B = [FR45B; FR45Bcell{i}]; end
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( FR45A( :, n), FR45B( :, n),'tail','both'); end
idCtxSel45=find(p<=0.05);

FR135Acell = FRall ( idx135A); FR135A=[]; for i = 1 : numel( FR135Acell); FR135A = [FR135A; FR135Acell{i}]; end
FR135Bcell = FRall ( idx135B); FR135B=[]; for i = 1 : numel( FR135Bcell); FR135B = [FR135B; FR135Bcell{i}]; end
p=zeros(cellnum,1); for n=1:cellnum;     p(n)=ranksum( FR135A( :, n), FR135B( :, n),'tail','both'); end
idCtxSel135=find(p<=0.05);

clear idCtxSel; idCtxSel = intersect( intersect( idCtxSel90, idCtxSel45), intersect( idCtxSel90, idCtxSel135) ) ;

% plot the results.
clear idtemp; figure;
% [~, idtemp] = sort( diffAB( idCtxSel), 'asc' ); % idtemp = [idtemp; idtemp; idtemp];
% idtemp1 =  idCtxSel ( idtemp( 1 : 20));  
idtemp1 = idCtxSel( 1 : 20);
aa = sig90A(:,  idtemp1 );
dd=aa./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 1)
plot(  cc' ); axis tight; title('90A'); hold on

bb = sig90B(:,  idtemp1 );
dd=bb./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 2)
plot(  cc' ); axis tight; title('90B'); hold on

aa = sig45A(:,  idtemp1 );
dd=aa./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 3)
plot(  cc' ); axis tight; title('45A'); hold on

bb = sig45B(:,  idtemp1 );
dd=bb./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 4)
plot(  cc' ); axis tight; title('45B'); hold on

aa = sig135A(:,  idtemp1 );
dd=aa./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 5)
plot(  cc' ); axis tight; title('135A'); hold on

bb = sig135B(:,  idtemp1 );
dd=bb./max(aa,[],1); cc = dd' + (1 : 20)';
subplot( 1, 6, 6)
plot(  cc' ); axis tight; title('135B'); hold on
%--------------------------------------------------------
% calculate the mean <FR> for each cells by context and orientation
FR45Amean = mean( FR45A, 1); FR45Amean = FR45Amean( idCtxSel);
FR45Bmean = mean( FR45B, 1); FR45Bmean = FR45Bmean( idCtxSel);
FR90Amean = mean( FR90A, 1); FR90Amean = FR90Amean( idCtxSel);
FR90Bmean = mean( FR90B, 1); FR90Bmean = FR90Bmean( idCtxSel);
FR135Amean = mean( FR135A, 1); FR135Amean = FR135Amean( idCtxSel);
FR135Bmean = mean( FR90B, 1); FR135Bmean = FR135Bmean( idCtxSel);
yDataA = [FR45Amean', FR90Amean', FR135Amean'];
yDataB = [FR45Bmean', FR90Bmean', FR135Bmean'];
%--------------------------------------------------------
% plot the <FR> mean
figure( 'name', ' FR mean, Context selective for each orientation', ...
    'Position', [ 300, 200, 800, 600 ]);
title('Context selective for each orientation');
% plot( 1:3, yDataA(1, : )); hold on; % plot( 1:3, yDataB(1, : )); hold on;
tab = uitabgroup; tabsubplot = 36;
ntab = ceil( size( yDataA,1) / tabsubplot);
for k = 1 : ntab
    thistab = uitab( tab, 'title', num2str(k));
    axes('Parent',thistab); 
    row = 6; col = 6;
    for i = 1 : row * col
        cellid = i + tabsubplot*(k-1);
        if ( cellid) > size( yDataA,1); break; end        
        subplot( row, col, i);     
        plot( 1:3, yDataA( cellid, : ), 'r-o'); hold on;
        plot( 1:3, yDataB( cellid, : ), 'b-o'); hold on;
        xticklabels(  {'45'; '90'; '135'});
        xlim([0.5 3.5]);
        ylimR = ylim;
        ylim( [  ylimR(1) - max( ylimR(1) * 0.15, 0.2), ylimR(2) * 1.15]);
        title(num2str( idCtxSel( cellid)));   
    end
end

%% example cells
figure( 'name', ' FR mean, Context selective for each orientation', ...
    'Position', [ 300, 200, 800, 100 ]);
title('Example cells');
% plot( 1:3, yDataA(1, : )); hold on; % plot( 1:3, yDataB(1, : )); hold on;
cellids = [ 7, 131, 132, 142, 173, 178, 220, 231, 410, 211];
for i = 1 : numel( cellids)
    cellid = find( idCtxSel == cellids(i));     
    subplot( 1, numel( cellids), i);     
    plot( 1:3, yDataA( cellid, : ), 'r-o'); hold on;
    plot( 1:3, yDataB( cellid, : ), 'b-o'); hold on;
    xticklabels(  {'45'; '90'; '135'});
    xlim([0.5 3.5]);
    ylimR = ylim;
    ylim( [  ylimR(1) - max( ylimR(1) * 0.15, 0.2), ylimR(2) * 1.15]);
    title( num2str( cellids(i)) );   
end


%%








