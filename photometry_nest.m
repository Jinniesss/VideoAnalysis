clear all;

%%
load('check_FP\phot_timehourcrop.mat','phot_timehourcrop');  % hour
load("check_FP\photometry.mat",'photometry');          
load("check_FP\labels.mat",'labels');  % 1/2/3
load("check_FP\labels_timecrop.mat",'labels_timecrop');     % hour
labels = labels.';

folder = pwd;
[~,name,~] = fileparts(folder);

% initialize
freq = 10; % frames per sec

% load dataframe
csv_fname = fullfile(folder, [name '_data.csv']);
data = readtable(csv_fname);
nest_state = data.nest.';
% In nest: 1; Out of nest: 0; Low-likelihood: NaN

frame_len = length(nest_state);
nest_state_diff = diff(nest_state);
nest_state_change_frame = find(nest_state_diff ~= 0);   % index of frame
nest_state_change_frame = horzcat(nest_state_change_frame,frame_len);

labels_len = length(labels_timecrop);
labels_diff = diff(labels);
labels_change = find(labels_diff ~= 0);     % index of 5s bout
labels_change = horzcat(labels_change,labels_len);  

labels_change_frame = labels_timecrop(labels_change)*3600*freq;  % index of frame
labels_change_frame(end) = labels_change_frame(end) +5*freq;

slice_start = 0;
slice_end = 0;
in_phot_all = [];
out_phot_all = [];
in_1_all = [];
in_2_all = [];
in_3_all = [];
out_1_all = [];
out_2_all = [];
out_3_all = [];

state_change_frame = horzcat(nest_state_change_frame,labels_change_frame);
state_change_frame = unique(state_change_frame);
state_change_frame = sort(state_change_frame);


for i = 1:length(state_change_frame)
    slice_start = slice_end+1;          % frame
    slice_end = state_change_frame(i);
    if slice_start > length(nest_state)
        break;
    end
    slice_end = min(slice_end,length(nest_state));
    cur_nest_state = nest_state(int32(slice_start));
    label_idx = labels_change(find(labels_change_frame>=slice_start,1));
    if isempty(label_idx)
        continue;
    end
    cur_label = labels(label_idx);
    if isnan(cur_nest_state)
        continue;
    end
    
    slice_start_hour = slice_start/freq/3600; % hour
    slice_end_hour = slice_end/freq/3600;
    
    if or(slice_end_hour < phot_timehourcrop(1),slice_start_hour > phot_timehourcrop(end))
        continue;
    end

    slice_start_hour = max(phot_timehourcrop(1),slice_start_hour);
    slice_end_hour = min(phot_timehourcrop(end),slice_end_hour);

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
        case 1
            in_phot_all = horzcat(in_phot_all , photometry(phot_start_ind:phot_end_ind));
            
            switch cur_label
                case 1
                    in_1_all = horzcat(in_1_all,photometry(phot_start_ind:phot_end_ind));
                case 2 
                    in_2_all = horzcat(in_2_all,photometry(phot_start_ind:phot_end_ind));
                case 3
                    in_3_all = horzcat(in_3_all,photometry(phot_start_ind:phot_end_ind));
            end

        case 0
            out_phot_all = horzcat(out_phot_all , photometry(phot_start_ind:phot_end_ind));

            switch cur_label
                case 1
                    out_1_all = horzcat(out_1_all,photometry(phot_start_ind:phot_end_ind));
                case 2 
                    out_2_all = horzcat(out_2_all,photometry(phot_start_ind:phot_end_ind));
                case 3
                    out_3_all = horzcat(out_3_all,photometry(phot_start_ind:phot_end_ind));
            end

        otherwise
            disp('error: nest state');
            disp(cur_nest_state)
    end
end


%% plot
fig = figure('Position', [100, 100, 1200, 800]);

% Compute mean and standard variation
mean1 = mean(in_phot_all);
mean2 = mean(out_phot_all);
sd1 = std(in_phot_all)/sqrt(numel(in_phot_all));
sd2 = std(out_phot_all)/sqrt(numel(out_phot_all));

ax = subplot(2,3,1);
hold(ax, 'on');
bar(ax, [1, 2], [mean1, mean2]);
hold(ax, 'off');

% Plot error bars for standard deviation
hold(ax, 'on');
errorbar(ax, [1, 2], [mean1, mean2], [sd1, sd2], '.', 'LineWidth', 1);
hold(ax, 'off');

% Customize the plot
xlabel('Nest State');
ylabel('Photometry');
xticks(ax, [1, 2]);
xticklabels(ax, {'In Nest', 'Out of Nest'});
grid(ax, 'off');

%% 
mean1 = mean(in_1_all);
mean2 = mean(in_2_all);
mean3 = mean(in_3_all);
sd1 = se(in_1_all);
sd2 = se(in_2_all);
sd3 = se(in_3_all);

ax2 = subplot(2,3,2);
hold(ax2, 'on');
bar(ax2, [1, 2,3], [mean1, mean2,mean3]);
hold(ax2, 'off');

% Plot error bars for standard deviation
hold(ax2, 'on');
errorbar(ax2, [1, 2,3], [mean1, mean2,mean3], [sd1, sd2,sd3], '.', 'LineWidth', 1);
hold(ax2, 'off');

% Customize the plot
xlabel('Brain State');
ylabel('Photometry');
xticks(ax2, [1, 2,3]);
xticklabels(ax2, {'REM', 'WAKE','NREM'});
grid(ax2, 'off');
title('In Nest')
% saveas(gcf, [name '_phot_in_nest.png']);
%%
mean1 = mean(out_1_all);
mean2 = mean(out_2_all);
mean3 = mean(out_3_all);
sd1 = std(out_1_all)/sqrt(numel(out_1_all));
sd2 = std(out_2_all)/sqrt(numel(out_2_all));
sd3 = std(out_3_all)/sqrt(numel(out_3_all));

ax1 = subplot(2,3,3);
hold(ax1, 'on');
bar(ax1, [1, 2,3], [mean1, mean2, mean3]);
hold(ax1, 'off');

% Plot error bars for standard deviation
hold(ax1, 'on');
errorbar(ax1, [1, 2,3], [mean1, mean2, mean3], [sd1, sd2, sd3], '.', 'LineWidth', 1);
hold(ax1, 'off');

% Customize the plot
xlabel('Brain State');
ylabel('Photometry');
xticks(ax1, [1, 2, 3]);
xticklabels(ax1, {'REM', 'WAKE', 'NREM'});
grid(ax1, 'off');
title('Out of Nest');


%%
subplot(2,3,5)
data = [length(in_1_all) length(in_2_all) length(in_3_all)];
labels = {'REM','WAKE','NREM'};
pie(data)
legend(labels)
title('In Nest')
axis equal;

subplot(2,3,6)
data = [length(out_1_all) length(out_2_all) length(out_3_all)];
labels = {'REM','WAKE','NREM'};
pie(data)
legend(labels)
title('Out of Nest')
axis equal;

saveas(gcf, [name '_phot_ana.png']);

%%
data = [mean(in_1_all) mean(in_2_all) mean(in_3_all) mean(in_phot_all)
        se(in_1_all) se(in_2_all) se(in_3_all) se(in_phot_all)
        mean(out_1_all) mean(out_2_all) mean(out_3_all) mean(out_phot_all)
        se(out_1_all) se(out_2_all) se(out_3_all) se(out_phot_all)];
data = reshape(data.', 1, []);
variables = {'In_R_mean','In_W_mean','In_N_mean','In_mean'...
             'In_R_se','In_W_se','In_N_se','In_se'...
             'Out_R_mean','Out_W_mean','Out_N_mean','Out_mean',...
             'Out_R_se','Out_W_se','Out_N_se','Out_se'};

phot_ana = array2table(data,'VariableNames',variables);
save([name '_phot_ana.mat'], 'phot_ana');

function se = se(vector)
    n = numel(vector);                % Number of data points
    sampleMean = mean(vector);        % Sample mean
    sampleStdDev = std(vector);       % Sample standard deviation
    se = sampleStdDev / sqrt(n);      % Standard error
end