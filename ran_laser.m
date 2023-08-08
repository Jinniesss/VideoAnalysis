clear;
load("laser_real/laser.mat","laser")
len = length(laser);
laser_r=zeros(len,1);
laser_r(1) = 1;
while true
    for i = 2:len
        laser_r(i) = laser_r(i-1) + (rand*(50)+40);
    end
    if max(laser_r)<=max(laser)
        break;
    end
end
save('laser_r.mat','laser_r')