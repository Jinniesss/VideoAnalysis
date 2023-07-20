clear all;

%%     
load("check_FP\labels.mat",'labels');  % 1/2/3 -- R/W/N
load("check_FP\labels_timecrop.mat",'labels_timecrop');     % hour
labels = labels.';

folder = pwd;
[~,name,~] = fileparts(folder);

% initialize
names = ["centerbody3","leftear","headstage"];
freq = 10; % frames per sec
rem_var = [];
nrem_var = [];
wake_var = [];

% load dataframe
csv_fname = fullfile(folder, [name '_data.csv']);
data = readtable(csv_fname);
s = size(data);
l = s(1);

for n = 1:numel(names)
    bpname = names(n);
    colname = strcat(bpname,'_movement_state');
    varname = strcat(bpname,'_var');
    var_traj = (data.(varname)).';
    labels_frame = zeros(1,l);
    mov_state_frame = zeros(1,l);
    if ismember(colname,data.Properties.VariableNames)
        data = removevars(data,colname);
    end
    %%
    for i = 1:length(var_traj)
        label_idx = find(labels_timecrop>i/freq/3600,1)-1;
        if label_idx == 0
            labels_frame(i) = 0;
            continue;
        end
        if isempty(label_idx)
            label_idx = length(labels_timecrop);
        end
    
        cur_var = var_traj(i);
        label = labels(label_idx);
    
        labels_frame(i) = label;
    
        if label == 1
            rem_var = horzcat(rem_var,cur_var);
        elseif label == 2
            wake_var = horzcat(wake_var,cur_var);
        elseif label == 3
            nrem_var = horzcat(nrem_var,cur_var);
        end
    end
    
    %%
    figure();
    hold on;
    xlim([0 10])
    width = 0.2;
    histogram(wake_var,'BinWidth',width,'FaceColor','auto');
    histogram(rem_var, 'BinWidth', width, 'FaceColor', 'blue');
    histogram(nrem_var,'BinWidth', width, 'FaceColor', 'red');
    legend()
    xlabel('Variance of Trajectory');
    ylabel('Frequency');
    title(bpname);
    set(gca, 'YScale', 'log');
    % close;
    %%
    sleep_var = horzcat(nrem_var,rem_var);
    s_sleep_var = sort(sleep_var, 'descend');
    t1 = s_sleep_var(round((length(s_sleep_var)/20)));
    % t1 = mean(sleep_var)+3*std(sleep_var);
    
    mov_state_frame(var_traj < t1) = 1;   % 1 -- immobility
    data = addvars(data, mov_state_frame.', 'NewVariableNames', strcat(bpname,'_movement_state'));
end
%%
if ismember('movement_state',data.Properties.VariableNames)
    data = removevars(data,'movement_state');
end
mov_state = zeros(1,l)+1;
for i = 1:l
    for n = 1:numel(names)
        bpname = names(n);
        state = data.(strcat(bpname,'_movement_state'));
        if state(i) == 0
            mov_state(i) = 0;
            break;
        end
    end
end
data = addvars(data, mov_state.', 'NewVariableNames', 'movement_state');
writetable(data, strcat(name,'_data.csv'));
