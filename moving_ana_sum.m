clear all;
% run this script at the mouse folder with session folders (e.g. M111)
path = pwd;
folders = dir(path);
folders = folders([folders.isdir]);  % Filter out non-folders
[~, mouse_name, ~] = fileparts(path);

time_in_nest = [];
time_out_of_nest = [];
moving_rate_in = [];
moving_rate_out = [];
moving_rate_tot = [];
sessions = [];
nest_area = [];
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
 
    time_in_nest = horzcat(time_in_nest, data.time_in_nest);
    time_out_of_nest = horzcat(time_out_of_nest , data.time_out_of_nest);

    moving_rate_in = horzcat(moving_rate_in,data.distance_in_nest / data.time_in_nest);
    moving_rate_out = horzcat(moving_rate_out,data.distance_out_of_nest / data.time_out_of_nest);
    moving_rate_tot = horzcat(moving_rate_tot, (data.distance_in_nest+data.distance_out_of_nest)/(data.time_in_nest+data.time_out_of_nest));
    
    s = get_session(folder);
    sessions = vertcat(sessions,s);

    nest_a = load([folder '_nest_area.mat']);
    nest_a = nest_a.nest_area;
    nest_area = horzcat(nest_area,nest_a);   % cm^2
    cd(path)
end


save([mouse_name '_moving_ana_summary.mat'],'sessions','nest_area','time_out_of_nest','time_in_nest','moving_rate_out','moving_rate_in','moving_rate_tot')

function num = get_session(str)
    matches = regexp(str, '[sS](\d+)', 'tokens', 'once');

    if ~isempty(matches)
        num = str2double(matches{1});
    else
        disp('No match found.');
    end
end