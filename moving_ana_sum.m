clear all;

path = pwd;
folders = dir(path);
folders = folders([folders.isdir]);  % Filter out non-folders
[~, mouse_name, ~] = fileparts(path);

time_in_nest = 0;
time_out_of_nest = 0;
distance_in_nest = 0;
distance_out_of_nest = 0;

for i = 1:numel(folders)
    if strcmp(folders(i).name, '.') || strcmp(folders(i).name, '..')
        continue;
    end
    folder = folders(i).name;
    containsNumber = any(regexp(folder, '\d', 'once'));
    if ~containsNumber 
        continue;
    end
    cd(folder);
    data = load([folder '_Moving_ana.mat']);
 
    time_in_nest = time_in_nest + data.time_in_nest;
    time_out_of_nest =  time_out_of_nest + data.time_out_of_nest;

    distance_in_nest = distance_in_nest + data.distance_in_nest;
    distance_out_of_nest = distance_out_of_nest + data.distance_out_of_nest;
    
    cd(path)
end

moving_rate_in = distance_in_nest / time_in_nest;
moving_rate_out = distance_out_of_nest / time_out_of_nest;
moving_rate_tot = (distance_out_of_nest+distance_in_nest) / (time_out_of_nest+time_in_nest);
save([mouse_name '_moving_ana_summary.mat'],'time_out_of_nest','time_in_nest','moving_rate_out','moving_rate_in','moving_rate_tot')
