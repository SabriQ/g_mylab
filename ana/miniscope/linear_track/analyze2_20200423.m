%% Quantify the Ctx / HD / Place cells
% 
clc; clear; close all; disp([mfilename, ': running....']);
%% load data
savepath = '\\10.10.46.135\Lab_Members\XuChun\Lab Projects\01_Intra Hippocampus\Miniscope_Linear_Track';
file1 = fullfile( savepath, 'Ctx_HD_PC.mat'); % load the Context, place and HD cells
load( file1);
% List of loaded Var
%  'idPCs' 'PC_SIs' 'idHDs' 'SelHDs', 'idCtxs','SelCtxs'
%  'FRposcells', 'Speedcells', 
%  'ltPC_SIs_shuffle', 'lt_PC_SItrials_shuffle',  'PC_SIs', 'PC_SItrials', 
%  'idHDs', 'idHDlefts','idHDrights', 'SelHDs', 
%  'idCtxs', 'idCtxAs','idCtxBs','SelCtxs','blocksequence',
%  'FRalls'
%% reorganize the cells's Ca2+ activities.  
% require <animaldata> 
%     idCtx = idCtxs{ n};   SelCtx = SelCtxs{ n};
%     idHD = idHDs{ n};   SelHD = SelHDs{ n};
%     idPC = idPCs{ n}; 
%     FRblock = FRalls{ n};
%     FRpos = FRposcells{ n};
% <totaldata> reorganize the cells's Ca2+ activities.

blocksequence = {'90A', '90B'; '90A2', '90B2';'90A3', '90B3'; '135A', '135B'; '45A', '45B'; '90AA', '90BB'}; % fixed block sequence for the convenience of analysis
% blocksequence = {'90A', '90B'; '90A2', '90B2';'90A3', '90B3'};
nfilenames = numel( animaldata);
[nsession, ~] = size( blocksequence);
ncontext = 2; % A vs. B.
nrunning = 2; % left vs. right
totaldata = cell( nfilenames, nsession, ncontext,  nrunning); % {ntrials} ( nFRpos, nneurons)
% -------------- collect the data ----------------
[idCtxH_HDHs, ... % neuron ID show both high Ctx and high HD selectivity
    idCtxH_HDnos, ... % only Context cells, but not HD cells
    SelCtx1, SelHD1 ... % selectivity index
    ]= deal( cell( nfilenames, nsession)); 
for n = 1 : nfilenames
    idCtx = idCtxs{ n};   SelCtx = SelCtxs{ n};
    idHD = idHDs{ n};   SelHD = SelHDs{ n};
    idPC = idPCs{ n}; 
    FRblock = FRalls{ n};
    FRpos = FRposcells{ n};
    blockname = animaldata{ n}.blockname;
    behavetrialblocks = animaldata{ n}.in_context_behavetrialblocks;
    for k = 1 : size( blocksequence,1)
        % in some animals, the session may be missing
        if ( sum( strcmp(blockname, blocksequence{k,1} ))==0 ...
                || sum( strcmp(blockname, blocksequence{k,2})) ==0 ) 
            idCtxH_HDHs{ n, k} = [];
            idCtxH_HDnos{ n, k} = [];
        else  % otherwise, get the data for this session       
            % get the intersection of cell ID            
            [~, idx] = sort( abs( SelCtx{ k} ( idCtx{k} )), 'descend'); idCtx_sort = idCtx{ k}( idx); % SelCtx is full size with NaN, idCtx is only Context selective cell ID
            [~, idx] = sort( abs( SelHD{ k} ( idHD{k} )), 'descend'); idHD_sort = idHD{ k}( idx);      
            idCtxH_HDHs{ n, k} = intersect( idCtx_sort, idHD_sort);
            idCtxH_HDnos{ n, k} = setdiff( idCtx_sort, idHD_sort); % only Context cells, but not HD cells
            SelCtx1{ n, k} = SelCtx{ k};
            SelHD1{ n, k} = SelHD{ k};
            % organize the data
            id1 = strcmp(blockname, blocksequence{k,1} ); % context A
            id2 = strcmp(blockname, blocksequence{k,2} ); % context B
            FRa= FRpos{ id1}; % trials { npos, neuros}
            FRb = FRpos{ id2}; 
            behavetrial1 = behavetrialblocks{ id1}; % trials { Ca trace x col25(running)}, ctxt A
            behavetrial2 = behavetrialblocks{ id2}; % context B
            
            % context A
            id1 = []; id2 = []; 
            for kk = 1 : numel( behavetrial1)
                if mean( behavetrial1{ kk}(:, 25)) ==1 % running left, 1
                    id1 = [id1; kk];
                elseif mean( behavetrial1{ kk}(:, 25))==0 % running right, 0
                     id2 = [id2; kk];
                end                        
            end
             totaldata{ n, k, 1, 1} = FRa( id1);
             totaldata{ n, k, 1, 2} = FRa( id2);                        
            
             % context B
             id1 = []; id2 = [];
            for kk = 1 : numel( behavetrial2)
                if mean( behavetrial2{ kk}(:, 25)) ==1 % running left, 1
                    id1 = [id1; kk];
                elseif mean( behavetrial2{ kk}(:, 25)) ==0 % running right, 0
                    id2 = [id2; kk];
                end                     
            end
             totaldata{ n, k, 2, 1} = FRb( id1);
             totaldata{ n, k, 2, 2} = FRb( id2);    
        end      
    end
end
save(file1, 'totaldata', '-append');

% [nfilenames, nsession, ncontext, nrunning] = size( totaldata);
matFRpos = []; % mat (:, [nfiles, nsession, id, FRpos(10)]). demension (nneuron, 3+10)
matFRposfull = []; %(:, [nfiles, nession, id,  ncontext, nrunning, FRpos(10)). dimension( n, 5+10), 
for i = 1 : nfilenames
    for j = 1 : nsession
            % sum them up across context
            % firing rate [npos, nneuron]
        meantmp = [];
        sumtmp2 = [];
        for k = 1 : ncontext
            % sum them up across running direction
            % firing rate [npos, nneuron]
            sumtmp1 = [];
            for m = 1 : nrunning
                % mean firing rate [npos, nneuron]
                % for various number of trials
                tmp1 = totaldata{ i, j, k, m};
                % reconstruct a matrix to compute mean
                if isempty( tmp1)
                    sumtmp2 = [];
                    sumtmp1 = [];
                    continue;
                end
                [row, col] = size( tmp1{1});
                tmp3 = nan( length( tmp1), row, col);
                for n = 1 : length( tmp1) % trials in this block
                    tmp3(n,:,:) = tmp1{ n};
                end
                meantmp1 = squeeze( nanmean( tmp3, 1)); % there may be NaN in the matrix.
                
                nneuron = size( meantmp1, 2);
                nfilenames_marks = ones( nneuron, 1) * i;
                nsession_marks = ones( nneuron, 1) * j;
                ncontext_marks = ones( nneuron, 1) * k;
                nrunning_marks = ones( nneuron, 1) * m;
                fullid = 1 : nneuron;
                tmp = [nfilenames_marks, nsession_marks, fullid', ncontext_marks, ...
                    nrunning_marks,  meantmp1'];
                matFRposfull = [ matFRposfull; tmp]; %#ok<AGROW>                    
                
                if m == 1
                    sumtmp1 = meantmp1;
                else
                    sumtmp1 = sumtmp1 + meantmp1; 
                end                    
            end
            if isempty( sumtmp1)
                continue;
            end
            if k == 1
                sumtmp2 = sumtmp1;
            else
                sumtmp2 = sumtmp2 + sumtmp1; 
            end
        end
        if isempty( sumtmp2)
            continue;
        end
        
        meantmp = sumtmp2 / ( ncontext * nrunning);
        if isempty( meantmp)
            continue;
        end

        nneuron = size( meantmp, 2);
        nfilenames_marks = ones( nneuron, 1) * i;
        nsession_marks = ones( nneuron, 1) * j;
        fullid = 1 : nneuron;
        tmp = [nfilenames_marks, nsession_marks, ...
            fullid', meantmp'];
        matFRpos = [ matFRpos; tmp]; %#ok<AGROW>    
    end
end
save(file1, 'matFRposfull', 'matFRpos', '-append');

%% organize Ctx, HD selectivity and Place cell SI  
% only select cells they are considered to have significant selectivity
% return [totalSelCtx, totalSelHD, totalPC_SI], [totalSelCtxHDpcSI]
% return <matSelCtxHDpcSI>
blocksequence = {'90A', '90B'; '90A2', '90B2';'90A3', '90B3'; '135A', '135B'; '45A', '45B'; '90AA', '90BB'}; 
nfilenames = numel( animaldata);
[nsession, ~] = size( blocksequence);

% -- pick out those significantly modulated cells by either feature
% totaldata = cell( nfilenames, nsession, ncontext,  nrunning); % {ntrials} ( nFRpos, nneurons)
[totalSelCtx, totalSelHD, totalPC_SI] ... 
    = deal( cell( nfilenames, nsession)); % mat ( [id, sel], nneuron) (2,nneuron)

nfiles = length( idCtxs);
for i = 1 : nfiles
    idCtxsess = idCtxs{ i}; 
    SelCtx = SelCtxs{ i};
    
    idHD = idHDs{ i};
    SelHD = SelHDs{ i};
    
    idPC = idPCs{ i};
    PC_SI = PC_SIs{ i};
    
    for j = 1 : nsession
        idtemp= idCtxsess{ j};
        Seltemp = SelCtx{ j};
        totalSelCtx{ i, j} = [ idtemp, Seltemp( idtemp)'];
        
        idtemp = idHD{ j};
        Seltemp = SelHD{ j};
        totalSelHD{ i, j} =  [ idtemp, Seltemp( idtemp)'];
        
        idtemp = idPC{ j};
        SItemp = PC_SI{ j};
        if isempty( SItemp)
            totalPC_SI{ i, j} = [];
        else
            totalPC_SI{ i, j} = [ idtemp, SItemp( idtemp)];
        end
    end
end % i = 1 : nfiles

% -- pick out those significantly modulated cells by three features
% totaldata = cell( nfilenames, nsession, ncontext,  nrunning); % {ntrials} ( nFRpos, nneurons)
[totalSelCtxHDpcSI] ... 
    = deal( cell( nfilenames, nsession)); % mat (nneuron, [id, selCtx, selHD, pcSI] ) (nneuron, 4)

% mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
matSelCtxHDpcSI = [];
matSelCtxHD = [];
matSelCtx = [];
matSelHD = [];
matSelCtxpcSI = [];
matSelHDpcSI = [];
matpcSI = [];

nfiles  = length( idCtxs);
for i = 1 : nfiles
    tmp = [];
    for j = 1 : nsession        
        if isempty( PC_SIs{ i}{ j})
            continue;
        end
        
        % find cells respond to all three features
        idtemp1 = intersect( idCtxs{ i}{ j}, idHDs{ i}{ j});
        idtemp2 = intersect( idHDs{ i}{ j}, idtemp1); % find the cell id selective for both context and HD
        idtemp3 = intersect( idPCs{ i}{ j}, idtemp2); % find the cell id selective for three
        totalSelCtxHDpcSI{ i, j} = [idtemp3, SelCtxs{ i}{ j}( idtemp3)', SelHDs{ i}{ j}( idtemp3)', PC_SIs{ i}{ j}( idtemp3)];   
        
        tmp = cell2mat( totalSelCtxHDpcSI( i, j));        % transform into matrix
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelCtxHDpcSI = [matSelCtxHDpcSI; tmp2]; %#ok<AGROW>
        
        % find cells respond to context and HD
        idtemp1 = intersect( idCtxs{ i}{ j}, idHDs{ i}{ j});
        idtemp2 = setdiff( idtemp1, idPCs{i}{j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelCtxHD = [ matSelCtxHD; tmp2]; %#ok<AGROW>
        
        % find cells repsond to context only
        idtemp1 = setdiff( idCtxs{ i}{ j}, idHDs{ i}{ j});
        idtemp2 = setdiff( idtemp1, idPCs{i}{j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelCtx = [ matSelCtx; tmp2]; %#ok<AGROW>
        
        % find cells repsond to HD only
        idtemp1 = setdiff( idHDs{ i}{ j}, idCtxs{ i}{ j});
        idtemp2 = setdiff( idtemp1, idPCs{i}{j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelHD = [ matSelHD; tmp2]; %#ok<AGROW>
        
        % find cells respond to Context and Place fileds
        idtemp1 = intersect(  idPCs{i}{j}, idCtxs{ i}{ j});
        idtemp2 = setdiff( idtemp1,idHDs{ i}{ j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelCtxpcSI = [ matSelCtxpcSI; tmp2];       %#ok<AGROW>
        
        % find cells respond to HD and place fields
        idtemp1 = intersect(  idPCs{i}{j}, idHDs{ i}{ j});
        idtemp2 = setdiff( idtemp1, idCtxs{ i}{ j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matSelHDpcSI = [ matSelHDpcSI; tmp2];       %#ok<AGROW>
        
        % find cells repsond to place field only
        idtemp1 = setdiff(  idPCs{i}{j}, idCtxs{ i}{ j});
        idtemp2 = setdiff( idtemp1, idHDs{ i}{ j});
        tmp = ( [idtemp2, SelCtxs{i}{j}(idtemp2)', SelHDs{ i}{ j}( idtemp2)', PC_SIs{ i}{ j}( idtemp2)]);   
        tmp2 = [ ones( size( tmp, 1), 1) * i, ones( size( tmp, 1), 1) * j, tmp]; % mat (nneuron, [nfiles, nsession, id, selCtx, selHD, pcSI]) demension (nneuron, 6)
        matpcSI = [ matpcSI; tmp2]; %#ok<AGROW>
        
    end
end

% combine the FRpos into <matSelCtxHDpcSI> 
% return <matSelCtxpcSI> (:, [nfiles, nsession, id, SelCtx, selHD, pcSI, pos 7:16]
idx = ismember( matFRpos(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
placedata = matFRpos( idx, :);
placedata_sort = sortrows( placedata, [ 1 2 3]);
matSelCtxHDpcSI_sort = sortrows( matSelCtxHDpcSI, [1 2 3]);
matSel_Place =[matSelCtxHDpcSI_sort, placedata_sort(  :, 4:13)]; 

save(file1, 'matSelCtxHDpcSI', 'matSel_Place', ...
'matSelCtxHD', 'matSelCtx', 'matSelHD', ...
'matSelCtxpcSI', 'matSelHDpcSI', ...
'matpcSI', '-append');

%% plot the relatipnship bewteen Ctx, HD selectivity.   
% Show the correlation between Context selectivity, HD selectivy
% and Normalized spatial information.

figure('Position',[ 300, 300, 480, 400]);
xData = matSelCtxHDpcSI(:, 4);
yData = matSelCtxHDpcSI(:, 5);
cData = matSelCtxHDpcSI(:, 6);
[~, idx] = sort( cData);
C = jet( length( cData));
scatter( xData, yData, 30, C(idx,:));
ax = gca;
% ax.XAxisLocation = 'origin';
% ax.YAxisLocation = 'origin';
box on
xline( 0, ':');
yline( 0, ':');
ax.XLim = [-1.1 1.1];
ax.YLim = [ -1.1 1.1];
xticks([ -1, -0.5, 0, 0.5, 1]);
yticks([ -1, -0.5, 0, 0.5, 1]);
xlabel( 'Context Selectivity');
ylabel('Head Direction Selectivity');
colormap(C); 
c = colorbar; 
c.Label.String = 'Spatial information (Nor.)';

% ---- show ABS 
figure('Position',[ 300, 300, 480, 400]);
xData = abs( matSelCtxHDpcSI(:, 4));
yData = abs( matSelCtxHDpcSI(:, 5));
cData =  matSelCtxHDpcSI(:, 6); % spatial info.
[~, idx] = sort( cData);
C = jet( length( cData));
scatter( xData, yData, 30, C(idx,:));
ax = gca;
% ax.XAxisLocation = 'origin';
% ax.YAxisLocation = 'origin';
box on
xline( 0, ':');
yline( 0, ':');
ax.XLim = [0 1.02];
ax.YLim = [ 0 1.02];
xticks([ -1, -0.5, 0, 0.5, 1]);
yticks([ -1, -0.5, 0, 0.5, 1]);
xlabel( 'Context Selectivity');
ylabel('Head Direction Selectivity');
colormap(C); 
c = colorbar; 
c.Label.String = 'Spatial information (Nor.)';

% -- show spatial information distribution
figure('Position',[ 300, 300, 480, 400]);
% spatial info.
cData =  [matSelCtxHDpcSI(:, 6); matSelCtxpcSI(:,6); matSelHDpcSI(:,6); matpcSI(:,6)];
histogram( myNormalize(cData, 'Dim', 'col'), 30, 'Normalization','Probability');
title( 'All Spatial Information Distribution');

%% plot the distribution of Place fields.   
% For the cells with Ctx and PC features, their place fileds distribution 
% For all the PC cells, they have space fields distribution
% require <matSelCtxHDpcSI> & <mat....>
% retrun <matFRposPCall> , <matFRposCtxPC>

% ---- get FRpos for all the cells with PC features
idx1 = ismember( matFRpos(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
idx2 = ismember( matFRpos(:, [1 2 3]), matSelCtxpcSI( :, [1 2 3]), 'rows' );
idx3 = ismember( matFRpos(:, [1 2 3]), matSelHDpcSI( :, [1 2 3]), 'rows' );
idx4 = ismember( matFRpos(:, [1 2 3]), matpcSI( :, [1 2 3]), 'rows' );
matFRposPCall = matFRpos( idx1 | idx2 | idx3 | idx4, 1 : 13)';
FRpos1m = matFRposPCall( 4:13, :);
[nbin, nCell ] = size( FRpos1m);

% ---- define place field for each cell. 
% find the max bin and continuning bin >90% max value.
PCfield = NaN( 3, nCell); % 1, indmax; 2, binIDleft(borader not included); 3, binIDright (borader not incl.)
[FRpos1meanmax,indmax] = max( FRpos1m, [], 1); % the frame ID for peak response
PCfield( 1, :) = indmax;
idPC1 = 1 : length( indmax);
for o = idPC1
    idxtmp = indmax( o);
    for p = idxtmp : -1 : 1
        if FRpos1m( p, o) < FRpos1m( idxtmp, o) * 0.9
            PCfield( 2, o) = p;
            break;
        end
    end
    for q = idxtmp : nbin
        if FRpos1m( q, o) < FRpos1m( idxtmp, o) * 0.9
            PCfield( 3, o) = q;
            break;
        end
    end
end     

% ---- screen the place cell with place field criteria
% exclude place field > 30% of whole track
idxtmp = find( PCfield( 3, :) - PCfield( 2, :) > 0.3 * nbin );      
idPC1 = setdiff( idPC1, idxtmp);      

% exclude max FR < 0.1
idxtmp = find( FRpos1meanmax < 0.1);
idPC1 = setdiff( idPC1, idxtmp);

% update the FRpos matrix after excl. 
matFRposPCall = matFRposPCall( :, idPC1)'; % [ nCell, nbin]

% get the FRpos matrix for the cells with Ctx and PC feature
% MaxFRpos for all the PC cells
idx1 = ismember( matFRposPCall(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
idx2 = ismember( matFRposPCall(:, [1 2 3]), matSelCtxpcSI( :, [1 2 3]), 'rows' );
matFRposCtxPC = matFRposPCall( idx1 | idx2,  1:13);
% find the max bin
[~, indmaxPC] = max( matFRposPCall(:, 4:13), [], 2);
[~, indmaxCtxPC] = max( matFRposCtxPC(:, 4:13), [], 2);

 % ---- plot 
figure('Position', [ 300, 300, 480, 400]);
% scatter( CtxSelData, MaxFRposData, 30);
hold on
histogram( indmaxPC, 'Normalization','probability');
histogram( indmaxCtxPC, 'Normalization','probability');
ax = gca;
box on
xline( 0, ':');
yline( 0, ':');
ax.XLim = [ -0.1 11];
xlabel('MaxFR Bin');
legend({'All Place Cells';'Place & Context Cells'}, 'Location','North');

%% plot the place cell map,  each session has a mean  
%  require matSelCtxHDpcSI, matFRpos

% matFRpos = []; % mat ([nfiles, nsession, id, FRpos(10)]) demension (nneuron, 2+10)
% find indices that <matFRpos> share same as <matSelCtxHDpcSI>
idx = ismember( matFRpos(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
placedata = matFRpos( idx, 4:13);
[~,indmax]=max(placedata,[],2); % the frame ID for peak response
[~,indsort]=sort(indmax);
% placedata1 = zscore( placedata( indsort, :), [], 2);

figure('name', 'all the Ctx/HD cells');
imagesc( myNormalize( placedata( indsort, :)));
% imagesc(placedata1);

xlabel('Position','FontName','Times New Roman','Fontsize',14,'FontWeight','bold');
ylabel('Neurons','FontName','Times New Roman','Fontsize',14,'FontWeight','bold');
title('Place cells with both Ctx and HD feature') ;
set(get(gca,'title'),'FontSize',18,'FontWeight','bold','FontName','Times New Roman');


%% plot the place cell map, based on  Ctx Sel index for A and B   
% - make for subgroup, separ, top pannels show A preferring, 
% bottom pannels are B preferring

% require <matSelCtxHDpcSI>, <matFRposfull>
% matFRposfull = []; %(:, [nfiles, nession, id,  ncontext, nrunning, FRpos(10)).
idx = ismember( matFRposfull(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
placedata = matFRposfull( idx, :);

% separate the plot for Ctx A and Ctx B cells, avearge HD
% context A
placedata0 = placedata( placedata(:,4) == 1, :);
idx1 = placedata0(:, 5) == 1; % running 1
idx2 = placedata0(:, 5) == 2; % running 2
% avearge both HD for each cells , each context
placedataA = (placedata0( idx1, 6:15) + placedata0( idx2, 6:15) ) / 2;
% make sure placedataA are the same order as <matSelCtxHDpcSI>
[~, idx_sortdata] = sortrows( placedata0( idx1, 1:3), [1 2 3]);
placedataA =placedataA( idx_sortdata, :);

% context B
placedata0 = placedata( placedata(:,4) == 2, :);
idx1 = placedata0(:, 5) == 1; % running 1
idx2 = placedata0(:, 5) == 2; % running 2
% avearge both HD for each cells , each context
placedataB = (placedata0( idx1, 6:15) + placedata0( idx2, 6:15) ) / 2;
% make sure placedataB are the same order as <matSelCtxHDpcSI>
[~, idx_sortdata] = sortrows( placedata0( idx1, 1:3), [1 2 3]);
placedataB =placedataB( idx_sortdata, :);

% make sure <matSelCtxHDpcSI> is also sorted.
[matSelCtxHDpcSI1, ~] = sortrows( matSelCtxHDpcSI, [1 2 3]); 

% find the max of each row including both A and B.
max1 = max( [placedataA, placedataB],[], 2);

placedataA = myNormalize( placedataA, 'Methods', 'nor', 'norArray', max1);
placedataB = myNormalize( placedataB, 'Methods', 'nor', 'norArray', max1);

% sort by <dataA> peak for plotting
[~,indmax]=max(placedataA,[],2); % the frame ID for peak response
% [~,indmax]=max(placedataB,[],2); % the frame ID for peak response
[~,indsort]=sort(indmax);
% sort the Sel index accordingly
matSelCtxHDpcSI1 = matSelCtxHDpcSI1( indsort, :);

% % filter the place data
% Ga=fspecial('gaussian',3,2);
% for i=1:size( placedataA, 1)
%     placedataA(i,:)=imfilter( placedataA(i,:),Ga,'replicate'); 
%     placedataB(i,:)=imfilter( placedataB(i,:),Ga,'replicate'); 
% end

% % 2-D gaussian filter the map
% n=2; s=0.05;                                                           
% x = -1/2:1/(n-1):1/2;
% [Y,X] = meshgrid(x,x);
% f = exp( -(X.^2+Y.^2)/(2*s^2) );
% f = f ./ sum(f(:));
% % FR_filtered=conv2(bin_FR,f,'same');
% % FR_filtered(isnan(FR_filtered))=0; 
% bin_FR = placedataA;
% for i=1:size( bin_FR, 1)      
%     FR_filtered=conv2(bin_FR(i,:),f,'same');
%     FR_filtered(isnan(FR_filtered))=0; 
%     bin_FR(i,:) = FR_filtered;     
% end
% placedataA = bin_FR;

% bin_FR = placedataB;
% for i=1:size( bin_FR, 1)      
%     FR_filtered=conv2(bin_FR(i,:),f,'same');
%     FR_filtered(isnan(FR_filtered))=0; 
%     bin_FR(i,:) = FR_filtered;     
% end
% placedataB = bin_FR;

% Now further divide these matrix into A and B based on <matSelCtxHDpcSI>
placedataA = placedataA( indsort, :);
placedataA1 = placedataA( matSelCtxHDpcSI1( :, 4) < 0, :);
placedataA2 = placedataA( matSelCtxHDpcSI1( :, 4) > 0, :);

placedataB = placedataB( indsort, :);
placedataB1 = placedataB( matSelCtxHDpcSI1( :, 4) < 0, :);
placedataB2 = placedataB( matSelCtxHDpcSI1( :, 4) > 0, :);

% - make for subgroup, separ, top pannels show A preferring, 
% bottom pannels are B preferring
figure('name', 'Place fileds in Context A and B, subgroup by CtxSel', ...
    'Position', [ 300 300 300 600]);
sgtitle('Place fileds in Context A and B');
row = 2; col = 7;
subplot(row, col, 1:3)
imagesc( placedataA1, [0 1])
title('A')

ax = subplot(row, col, 4:6);
imagesc( placedataB1, [0 1])
title('B')
ax.YTick = ([]);

ax=subplot(row, col, 7);
imagesc( matSelCtxHDpcSI1( matSelCtxHDpcSI1( :, 4) < 0, 4), [-1 1]) 
title('Sel');
ax.YTick = ([]);

subplot(row, col, 8:10)
imagesc( placedataA2, [0 1])
title('A')

ax=subplot(row, col, 11:13);
imagesc( placedataB2, [0 1])
title('B')
ax.YTick = ([]);

ax=subplot(row, col, 14);
imagesc( matSelCtxHDpcSI1( matSelCtxHDpcSI1( :, 4) > 0, 4), [-1 1]) 
title('Sel');
ax.XTick = ([]);
ax.YTick = ([]);

%% plot the place cell map, based on  HD Sel index for Left and Right   
% - make for subgroup, separ, top pannels show left preferring, 
% bottom pannels are right preferring

% require <matSelCtxHDpcSI>, <matFRposfull>
% matFRposfull = []; %(:, [nfiles, nession, id,  ncontext, nrunning, FRpos(10)).
idx = ismember( matFRposfull(:, [1 2 3]), matSelCtxHDpcSI( :, [1 2 3]), 'rows' );
placedata = matFRposfull( idx, :);

% separate the plot for HD left and HD right cells, avearge Context
% HD left
placedata0 = placedata( placedata(:,5) == 1, :);
idx1 = placedata0(:, 4) == 1; % context A
idx2 = placedata0(:, 4) == 2; % context B
% avearge both context for each cells , each HD
placedataL = (placedata0( idx1, 6:15) + placedata0( idx2, 6:15) ) / 2;
% make sure placedataL are the same order as <matSelCtxHDpcSI>
[~, idx_sortdata] = sortrows( placedata0( idx1, 1:3), [1 2 3]);
placedataL =placedataL( idx_sortdata, :);

% context B
placedata0 = placedata( placedata(:,5) == 2, :);
idx1 = placedata0(:, 4) == 1; % context A
idx2 = placedata0(:, 4) == 2; % context B
% avearge both context for each cells , each HD
placedataR = (placedata0( idx1, 6:15) + placedata0( idx2, 6:15) ) / 2;
% make sure placedataR are the same order as <matSelCtxHDpcSI>
[~, idx_sortdata] = sortrows( placedata0( idx1, 1:3), [1 2 3]);
placedataR =placedataR( idx_sortdata, :);

% make sure <matSelCtxHDpcSI> is also sorted.
[matSelCtxHDpcSI1, ~] = sortrows( matSelCtxHDpcSI, [1 2 3]); 

% find the max of each row including both Left and Right.
max1 = max( [placedataL, placedataR],[], 2);

placedataL = myNormalize( placedataL, 'Methods', 'nor', 'norArray', max1);
placedataR = myNormalize( placedataR, 'Methods', 'nor', 'norArray', max1);

% sort by <dataA> peak for plotting
% [~,indmax]=max(placedataL,[],2); % the frame ID for peak response
[~,indmax]=max(placedataR,[],2); % the frame ID for peak response
[~,indsort]=sort(indmax);
% sort the Sel index accordingly
matSelCtxHDpcSI1 = matSelCtxHDpcSI1( indsort, :);

% Now further divide these matrix into Left and Right- preferring based on <matSelCtxHDpcSI>
placedataL = placedataL( indsort, :);
placedataL1 = placedataL( matSelCtxHDpcSI1( :, 5) < 0, :);
placedataL2 = placedataL( matSelCtxHDpcSI1( :, 5) > 0, :);

placedataR = placedataR( indsort, :);
placedataR1 = placedataR( matSelCtxHDpcSI1( :, 5) < 0, :);
placedataR2 = placedataR( matSelCtxHDpcSI1( :, 5) > 0, :);

% - make for subgroup, separate, top pannels show Left preferring, 
% bottom pannels are Right preferring
figure('name', 'Place fileds in HD left and right, subgroup by HD Sel', ...
    'Position', [ 300 300 300 600]);
sgtitle('Place fileds in HD Left and Right');
row = 2; col = 7;
subplot(row, col, 1:3)
imagesc( placedataL1, [0 1])
title('Left')

ax = subplot(row, col, 4:6);
imagesc( placedataR1, [0 1])
title('Right')
ax.YTick = ([]);

ax=subplot(row, col, 7);
imagesc( matSelCtxHDpcSI1( matSelCtxHDpcSI1( :, 4) < 0, 4), [-1 1]) 
title('Sel');
ax.YTick = ([]);

subplot(row, col, 8:10)
imagesc( placedataL2, [0 1])
title('Left')

ax=subplot(row, col, 11:13);
imagesc( placedataR2, [0 1])
title('Right')
ax.YTick = ([]);

ax=subplot(row, col, 14);
imagesc( matSelCtxHDpcSI1( matSelCtxHDpcSI1( :, 4) > 0, 4), [-1 1]) 
title('Sel');
ax.XTick = ([]);
ax.YTick = ([]);









