
%%     
load("check_FP\labels.mat",'labels');  % 1/2/3 -- R/W/N
load("check_FP\labels_timecrop.mat",'labels_timecrop');     % hour
labels = labels.';

folder = pwd;
[~,name,~] = fileparts(folder);

% initialize
names = ["nose","headstage","leftear","rightear","centerbody2","centerbody3","centerbody4"];
bp_num = 7;
freq = 10; % frames per sec
rem_var = [];
nrem_var = [];
wake_var = [];

% load dataframe
csv_fname = fullfile(folder, [name '_data.csv']);
data = readtable(csv_fname);
s = size(data);
l = s(1);
new_data = table(data.nest,'VariableNames',{'nest'});
sleep_state = zeros(1,l);
for n = 1:numel(names)
    bpname = names(n);
    colname = strcat(bpname,'_movement_state');
    varname = strcat(bpname,'_var');
    var_traj = (data.(varname)).';
    labels_frame = zeros(1,l);
    mov_state_frame = zeros(1,l);
    
    %%
    for i = 1:length(var_traj)
        label_idx = find(labels_timecrop>i/freq/3600,1)-1;
        if label_idx == 0
            continue;
        end
        if isempty(label_idx)
            label_idx = length(labels_timecrop)-1;
        end
        label = labels(label_idx);
        if n==1
            sleep_state(i)=label;
        end
        cur_var = var_traj(i);
        if isnan(cur_var)
            continue;
        end
        
    
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
    xmax = 1;
    xlim([0 xmax])
    bwidth = xmax/100;
    histogram(wake_var,'BinWidth', bwidth,'FaceColor','auto');
    histogram(rem_var, 'BinWidth', bwidth, 'FaceColor', 'blue');
    histogram(nrem_var,'BinWidth', bwidth, 'FaceColor', 'red');

    sleep_var = horzcat(nrem_var,rem_var);
    s_sleep_var = sort(sleep_var, 'descend');
    t1 = s_sleep_var(floor( length(s_sleep_var)*(1-0.95) ));
    t2 = max(sleep_var);
    % t1 = mean(sleep_var)+3*std(sleep_var);
    plot(t1,0,'o','MarkerSize', 10);
    plot(t2,0,'o','MarkerSize', 10);

    legend()
    xlabel('Variance of Trajectory');
    ylabel('Frequency');
    title(bpname);
    set(gca, 'YScale', 'log');

    mov_state_frame(var_traj < t1) = 1;     % 1 -- immobility
    mov_state_frame(var_traj > t2) = 2;     % 2 -- locomotion
    mov_state_frame(isnan(var_traj)) = NaN; %   -- low-likelihood
    
    % if ismember(colname,data.Properties.VariableNames)
    %     data = removevars(data,colname);
    % end
    new_data = addvars(new_data, mov_state_frame.', 'NewVariableNames', strcat(bpname,'_movement_state'));
    if n==1
        if ismember('sleep_state',new_data.Properties.VariableNames)
            new_data = removevars(new_data,'sleep_state');
        end
        new_data = addvars(new_data, sleep_state.', 'NewVariableNames','sleep_state');
    end
end
%%
if ismember('movement_state',new_data.Properties.VariableNames)
    new_data = removevars(new_data,'movement_state');
end
mov_state = zeros(1,l);
for i = 1:l
    states = zeros(1,bp_num);
    for n = 1:numel(names)
        bpname = names(n);
        state = new_data.(strcat(bpname,'_movement_state'));
        states(n) = state(i);
    end
    if sum(isnan(states)) >= bp_num-1
        mov_state(i) = -1;
        continue;
    end
    if sum(states==2)>1 && sum(states==2)+sum(isnan(states)) >= bp_num-1
        mov_state(i) = 2;
        continue;
    end
    if sum(states==1)>1 && sum(states==1)+sum(isnan(states)) >= bp_num-1
        mov_state(i) = 1;
    end
end
%% remove bouts
mov_state_diff = diff(mov_state);
mov_state_change_frame = find(mov_state_diff ~= 0);  % index of the last frame of each segment
mov_state_change_frame = horzcat(mov_state_change_frame,length(mov_state));
bouts_thre = 10;
for bout_thre = 1:bouts_thre
    bout_len = horzcat(mov_state_change_frame(1), diff(mov_state_change_frame));
    ind_bouts_tbr = find(bout_len<=bout_thre);
    for i = 1:numel(ind_bouts_tbr)
        bout_num = ind_bouts_tbr(i);
        if bout_num == 1
            continue;
        end
        bout_first = mov_state_change_frame(bout_num-1)+1;
        bout_last = mov_state_change_frame(bout_num);
        if mov_state(bout_first-1)==-1
            continue;
        elseif bout_last == length(mov_state)
            continue;
        end

        % if mov_state(bout_first-1) == mov_state(bout_last+1)
        mov_state(bout_first:bout_last) = mov_state(bout_first-1);
        % end
    end
end
%%
new_data = addvars(new_data, mov_state.', 'NewVariableNames', 'movement_state');
writetable(new_data, strcat(name,'_mov_state.csv'));
disp('[file updated]')