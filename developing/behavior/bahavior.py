from mylab.Cfile import LinearTrackBehaviorFile 

F = LinearTrackBehaviorFile(r"LickWater-test-201033-20200816-171112_log.csv")

print(F.choice)
print(F.reward)
print(F.Enter_Context)
print(F.data["Enter_ctx"])