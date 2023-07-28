
load('check_FP\phot_timehourcrop.mat','phot_timehourcrop');  % hour
load("check_FP\photometry.mat",'photometry');          
load("check_FP\labels.mat",'labels');  % 1/2/3
load("check_FP\labels_timecrop.mat",'labels_timecrop');     % hour
addpath("H:\My Drive\workstation\BehaviorAnalysis\functions\")
labels = labels.';
if old_data == 1
    phot_timehourcrop = phot_timehourcrop/60;
end

folder = pwd;
[~,name,~] = fileparts(folder);

% initialize
freq = 10; % frames per sec

% load dataframe
csv_fname_p = fullfile(folder, [name '_mov_state.csv']);
if ~exist(csv_fname_p, 'file') || redo==1
    disp(name);
    disp('clustering...');
    clustering();
end
data_n = readtable(csv_fname_p);
nest_state = data_n.nest.';
% In nest: 1; Out of nest: 0; Low-likelihood: NaN
mov_state = data_n.movement_state.';

frame_len = length(nest_state);
nest_state_diff = diff(nest_state);
nest_state_change_frame = find(nest_state_diff ~= 0);   % index of frame
nest_state_change_frame = horzcat(nest_state_change_frame,frame_len);

mov_state_diff = diff(mov_state);
mov_state_change_frame = find(mov_state_diff ~= 0);   % index of frame
mov_state_change_frame = horzcat(mov_state_change_frame,frame_len);

labels_len = length(labels);
labels_diff = diff(labels);
labels_change = find(labels_diff ~= 0);     % index of 5s bout
labels_change = horzcat(labels_change,labels_len-1);  

labels_change_frame = labels_timecrop(labels_change)*3600*freq;  % index of frame
labels_change_frame(end) = labels_change_frame(end) +5*freq;    % 5--bout length of labels

slice_start = 0;
slice_end = 0;
in_loco_all = [];in_nonl_all = [];in_immo_all = [];out_loco_all = [];out_nonl_all = [];out_immo_all = [];
in_nonl_r_all = [];in_nonl_w_all = [];in_nonl_n_all = [];in_immo_r_all = [];in_immo_w_all = [];in_immo_n_all = [];
in_loco_r_all = [];in_loco_w_all = [];in_loco_n_all = [];out_nonl_r_all = [];out_nonl_w_all = [];out_nonl_n_all = [];
out_immo_r_all = [];out_immo_w_all = [];out_immo_n_all = [];out_loco_r_all = [];out_loco_w_all = [];out_loco_n_all = [];

t_LM = 0;   t_NL = 0;   t_QW = 0;

state_change_frame = horzcat(nest_state_change_frame,labels_change_frame,mov_state_change_frame);
state_change_frame = unique(state_change_frame);
state_change_frame = sort(state_change_frame);

error_frame = [];
error_num = 0;
for i = 1:length(state_change_frame)
    slice_start = slice_end+1;          % frame
    slice_end = state_change_frame(i);
    if slice_start > length(nest_state)
        break;
    end
    slice_end = min(slice_end,length(nest_state));

    cur_nest_state = nest_state(int32(slice_start));
    cur_mov_state = mov_state(int32(slice_start));
    label_idx = labels_change(find(labels_change_frame>=slice_start,1));
    if isempty(label_idx)
        continue;
    end
    cur_label = labels(label_idx);
    if isnan(cur_nest_state) || isnan(cur_mov_state) || isnan(cur_nest_state)
        continue;
    end
    
    slice_start_hour = slice_start/freq/3600; % hour
    slice_end_hour = slice_end/freq/3600;
    
    if or(slice_end_hour < phot_timehourcrop(1),slice_start_hour > phot_timehourcrop(end))
        continue;
    end

    slice_start_hour = max(phot_timehourcrop(1),slice_start_hour);
    slice_end_hour = min(phot_timehourcrop(end),slice_end_hour);
    slice_dur_hour =  0-slice_start_hour + slice_end_hour; 

    % find corresponding start/end timepoint in phot
    phot_start_ind = find(phot_timehourcrop>=slice_start_hour,1);
    phot_end_ind = find(phot_timehourcrop>slice_end_hour,1)-1;
    if isempty(phot_start_ind)
        continue;
    end
    if isempty(phot_end_ind)
        phot_end_ind = length(phot_timehourcrop);
        if phot_end_ind<phot_start_ind
            continue;
        end
    end
    
    switch cur_nest_state
        % in
        case 1 
            % in_phot_all = horzcat(in_phot_all , photometry(phot_start_ind:phot_end_ind));
            switch cur_mov_state
                case 0
                    in_nonl_all = horzcat(in_nonl_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            in_nonl_r_all = horzcat(in_nonl_r_all,photometry(phot_start_ind:phot_end_ind));
                        case 2
                            in_nonl_w_all = horzcat(in_nonl_w_all,photometry(phot_start_ind:phot_end_ind));
                        case 3
                            in_nonl_n_all = horzcat(in_nonl_n_all,photometry(phot_start_ind:phot_end_ind));
                    end
                case 1
                    in_immo_all = horzcat(in_immo_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            in_immo_r_all = horzcat(in_immo_r_all, photometry(phot_start_ind:phot_end_ind));
                        case 2
                            in_immo_w_all = horzcat(in_immo_w_all, photometry(phot_start_ind:phot_end_ind));
                        case 3
                            in_immo_n_all = horzcat(in_immo_n_all, photometry(phot_start_ind:phot_end_ind));
                    end
                case 2
                    in_loco_all = horzcat(in_loco_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            in_loco_r_all = horzcat(in_loco_r_all, photometry(phot_start_ind:phot_end_ind));
                        case 2
                            in_loco_w_all = horzcat(in_loco_w_all, photometry(phot_start_ind:phot_end_ind));
                        case 3
                            in_loco_n_all = horzcat(in_loco_n_all, photometry(phot_start_ind:phot_end_ind));
                    end
            end

        % out
        case 0
            % out_phot_all = horzcat(out_phot_all , photometry(phot_start_ind:phot_end_ind));
            switch cur_mov_state
                case 0 
                    out_nonl_all = horzcat(out_nonl_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            out_nonl_r_all = horzcat(out_nonl_r_all, photometry(phot_start_ind:phot_end_ind));
                        case 2
                            out_nonl_w_all = horzcat(out_nonl_w_all, photometry(phot_start_ind:phot_end_ind));
                        case 3
                            out_nonl_n_all = horzcat(out_nonl_n_all, photometry(phot_start_ind:phot_end_ind));
                    end
                case 1
                    out_immo_all = horzcat(out_immo_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            out_immo_r_all = horzcat(out_immo_r_all, photometry(phot_start_ind:phot_end_ind));
                        case 2
                            out_immo_w_all = horzcat(out_immo_w_all, photometry(phot_start_ind:phot_end_ind));
                        case 3
                            out_immo_n_all = horzcat(out_immo_n_all, photometry(phot_start_ind:phot_end_ind));
                    end
                case 2
                    out_loco_all = horzcat(out_loco_all,photometry(phot_start_ind:phot_end_ind));
                    switch cur_label
                        case 1
                            out_loco_r_all = horzcat(out_loco_r_all, photometry(phot_start_ind:phot_end_ind));
                        case 2
                            out_loco_w_all = horzcat(out_loco_w_all, photometry(phot_start_ind:phot_end_ind));
                        case 3
                            out_loco_n_all = horzcat(out_loco_n_all, photometry(phot_start_ind:phot_end_ind));
                    end
            end

        otherwise
            disp('error');
    end

    % check any loco/nonl during sleep
    if cur_label ~= 2 && cur_mov_state ~= 1
        error_num = error_num + slice_end - slice_start + 1;   % frame
        error_frame = horzcat(error_frame,slice_start/freq);   % unit: second
    end
    
    if cur_label == 2
        switch cur_mov_state
            case 1
                t_QW = t_QW + slice_dur_hour;
            case 0
                t_NL = t_NL + slice_dur_hour;
            case 2
                t_LM = t_LM + slice_dur_hour;
        end
    end
end
error_rate = error_num / frame_len;


%%
% data_s = [mean(in_loco_n_all), mean(in_loco_r_all), mean(in_loco_w_all);
%         mean(out_loco_n_all), mean(out_loco_r_all), mean(out_loco_w_all);
%         mean(in_nonl_n_all), mean(in_nonl_r_all), mean(in_nonl_w_all);
%         mean(out_nonl_n_all), mean(out_nonl_r_all), mean(out_nonl_w_all);
%         mean(in_immo_n_all), mean(in_immo_r_all), mean(in_immo_w_all);
%         mean(out_immo_n_all), mean(out_immo_r_all), mean(out_immo_w_all);];

in_LM = mean(horzcat(in_loco_n_all,in_loco_r_all,in_loco_w_all));
in_NL = mean(horzcat(in_nonl_n_all,in_nonl_r_all,in_nonl_w_all));
in_QW = mean(in_immo_w_all);
in_NREM = mean(horzcat(in_loco_n_all,in_nonl_n_all,in_immo_n_all));
in_REM = mean(horzcat(in_loco_r_all,in_nonl_r_all,in_immo_r_all));

out_LM = mean(horzcat(out_loco_n_all, out_loco_r_all, out_loco_w_all));
out_NL = mean(horzcat(out_nonl_n_all, out_nonl_r_all, out_nonl_w_all));
out_QW = mean(out_immo_w_all);
out_NREM = mean(horzcat(out_loco_n_all, out_nonl_n_all, out_immo_n_all));
out_REM = mean(horzcat(out_loco_r_all, out_nonl_r_all, out_immo_r_all));

total_LM = mean(horzcat(in_loco_n_all, in_loco_r_all, in_loco_w_all, out_loco_n_all, out_loco_r_all, out_loco_w_all));
total_NL = mean(horzcat(in_nonl_n_all, in_nonl_r_all, in_nonl_w_all, out_nonl_n_all, out_nonl_r_all, out_nonl_w_all));
total_QW = mean(horzcat(in_immo_w_all, out_immo_w_all));
total_NREM = mean(horzcat(in_loco_n_all, in_nonl_n_all, in_immo_n_all, out_loco_n_all, out_nonl_n_all, out_immo_n_all));
total_REM = mean(horzcat(in_loco_r_all, in_nonl_r_all, in_immo_r_all, out_loco_r_all, out_nonl_r_all, out_immo_r_all));

data_s = [in_LM, in_NL, in_QW, in_NREM, in_REM,...
          out_LM, out_NL, out_QW, out_NREM, out_REM,...
          total_LM, total_NL, total_QW, total_NREM, total_REM,...
          t_LM, t_NL, t_QW];

data_s = reshape(data_s.', 1, []);
% variables = {'in_loco_n_mean', 'in_loco_r_mean', 'in_loco_w_mean',...
%              'out_loco_n_mean', 'out_loco_r_mean', 'out_loco_w_mean',...
%              'in_nonl_n_mean', 'in_nonl_r_mean', 'in_nonl_w_mean',...
%              'out_nonl_n_mean', 'out_nonl_r_mean', 'out_nonl_w_mean',...
%              'in_immo_n_mean', 'in_immo_r_mean', 'in_immo_w_mean',...
%              'out_immo_n_mean', 'out_immo_r_mean', 'out_immo_w_mean'};
% 

variables = {'in_LM', 'in_NL', 'in_QW', 'in_NREM', 'in_REM',...
             'out_LM', 'out_NL', 'out_QW', 'out_NREM', 'out_REM',...
             'total_LM', 'total_NL', 'total_QW', 'total_NREM', 'total_REM',...
             't_LM', 't_NL', 't_QW'};

phot_behv = array2table(data_s,'VariableNames',variables);
save([name '_phot_vs_beh.mat'], 'phot_behv');

%% In nest -- phot v.s. mov_states
figure();
set(gcf, 'Position', [100, 100, 1200, 400]);

ax2 = subplot(1,3,1);
hold(ax2, 'on');
bar(ax2, [1,2,3,4,5], [in_LM, in_NL,in_QW,in_NREM,in_REM]);
hold(ax2, 'off');

% Customize the plot
ylabel('Photometry');
xticks(ax2, [1,2,3,4,5]);
xticklabels(ax2, {'Locomotion', 'Non-locomotor','Quiet Wakefulness','NREM','REM'});
grid(ax2, 'off');
title('In Nest')
% saveas(gcf, [name '_phot_in_nest.png']);

%% Out of nest -- phot v.s. mov_states
ax1 = subplot(1,3,2);
hold(ax1, 'on');
bar(ax1, [1, 2,3,4,5], [out_LM, out_NL,out_QW,out_NREM,out_REM]);
hold(ax1, 'off');

% Customize the plot
ylabel('Photometry');
xticks(ax1, [1, 2, 3 ,4,5]);
xticklabels(ax1, {'Locomotion', 'Non-locomotor','Quiet Wakefulness','NREM','REM'});
grid(ax1, 'off');
title('Out of Nest');

%% 
subplot(1,3,3)
time_w = horzcat(t_LM,t_NL,t_QW);
bar(time_w);
ylabel('time(hour)');
title('Time of behavioral states during Wakefulness');
xticks(1:3);
xticklabels({'Locomotion', 'Non-locomotor', 'Quiet Wakefulness'});

saveas(gcf, [name '_phot_vs_behv.png']);