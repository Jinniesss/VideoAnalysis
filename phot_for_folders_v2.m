%%% sum z score

clear all; close all;

path = pwd;
folders = dir(path);
folders = folders([folders.isdir]);  % Filter out non-folders

zscore_sessions = [];
sessions = [];
flag = true;
m='';
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
    s = get_session(folder);
    sessions = vertcat(sessions,s);
    df_path = [folder '_zscore_ana.mat'];
    df = load(df_path);
    data = df.zscore_ana;
    zscore_sessions = vertcat(zscore_sessions,data);

    if flag
        m = get_mousename(folder);
        flag=false;
    end
    cd(path);
end

zscore_sessions.session = sessions;

save([m '_zscore_ana_summary.mat'],"zscore_sessions")

%% plot

fig = figure('Position', [100, 100, 1600, 400]);

% Compute mean and standard variation
mean1 = mean(zscore_sessions.In_mean);
mean2 = mean(zscore_sessions.Out_mean);
se1 = se(zscore_sessions.In_mean);
se2 = se(zscore_sessions.Out_mean);

ax = subplot(1,4,1);
hold(ax, 'on');
bar(ax, [1, 2], [mean1, mean2]);
hold(ax, 'off');

% Plot error bars for standard deviation
hold(ax, 'on');
errorbar(ax, [1, 2], [mean1, mean2], [se1, se2], '.', 'LineWidth', 1);
hold(ax, 'off');

% Customize the plot
xlabel('Nest State');
ylabel('z score');
xticks(ax, [1, 2]);
xticklabels(ax, {'In Nest', 'Out of Nest'});
grid(ax, 'off');

%% 
mean1 = mean(zscore_sessions.In_R_mean);
mean2 = mean(zscore_sessions.In_W_mean);
mean3 = mean(zscore_sessions.In_N_mean);
se1 = se(zscore_sessions.In_R_mean);
se2 = se(zscore_sessions.In_W_mean);
se3 = se(zscore_sessions.In_N_mean);

ax2 = subplot(1,4,2);
hold(ax2, 'on');
bar(ax2, [1, 2,3], [mean1, mean2,mean3]);
hold(ax2, 'off');

% Plot error bars for standard deviation
hold(ax2, 'on');
errorbar(ax2, [1, 2,3], [mean1, mean2,mean3], [se1, se2,se3], '.', 'LineWidth', 1);
hold(ax2, 'off');

% Customize the plot
xlabel('Brain State');
ylabel('zscore');
xticks(ax2, [1, 2,3]);
xticklabels(ax2, {'REM', 'WAKE','NREM'});
grid(ax2, 'off');
title('In Nest')
% saveas(gcf, [name '_zscore_in_nest.png']);
%%
zscore_sessions.Out_R_mean(isnan(zscore_sessions.Out_R_mean))=0;
zscore_sessions.Out_W_mean(isnan(zscore_sessions.Out_W_mean))=0;
zscore_sessions.Out_N_mean(isnan(zscore_sessions.Out_N_mean))=0;

mean1 = mean(zscore_sessions.Out_R_mean);
mean2 = mean(zscore_sessions.Out_W_mean);
mean3 = mean(zscore_sessions.Out_N_mean);
se1 = se(zscore_sessions.Out_R_mean);
se2 = se(zscore_sessions.Out_W_mean);
se3 = se(zscore_sessions.Out_N_mean);

ax1 = subplot(1,4,3);
hold(ax1, 'on');
bar(ax1, [1, 2,3], [mean1, mean2, mean3]);
hold(ax1, 'off');

% Plot error bars for standard deviation
hold(ax1, 'on');
errorbar(ax1, [1, 2,3], [mean1, mean2, mean3], [se1, se2, se3], '.', 'LineWidth', 1);
hold(ax1, 'off');

% Customize the plot
xlabel('Brain State');
ylabel('zscore');
xticks(ax1, [1, 2, 3]);
xticklabels(ax1, {'REM', 'WAKE', 'NREM'});
grid(ax1, 'off');
title('Out of Nest');

%%
% Compute mean and standard variation
mean1 = mean(zscore_sessions.In_W_mean);
mean2 = mean(zscore_sessions.Out_W_mean);
se1 = se(zscore_sessions.In_W_mean);
se2 = se(zscore_sessions.Out_W_mean);

ax = subplot(1,4,4);
hold(ax, 'on');
bar(ax, [1, 2], [mean1, mean2]);
hold(ax, 'off');

% Plot error bars for standard deviation
hold(ax, 'on');
errorbar(ax, [1, 2], [mean1, mean2], [se1, se2], '.', 'LineWidth', 1);
hold(ax, 'off');

% Customize the plot
xlabel('Nest State');
ylabel('zscore');
xticks(ax, [1, 2]);
xticklabels(ax, {'In Nest', 'Out of Nest'});
grid(ax, 'off');
title('WAKE')
%%

saveas(gcf, [m '_zscore_ana.png']);

function name = get_mousename(str)
    matches = regexp(str, '[Mm](\d+)', 'tokens', 'once');
    name='';
    if ~isempty(matches)
        num = (matches{1});
        name=['M' num];
    else
        disp('No match found.');
    end
end
function num = get_session(str)
    matches = regexp(str, '[sS](\d+)', 'tokens', 'once');

    if ~isempty(matches)
        num = str2double(matches{1});
    else
        disp('No match found.');
    end
end
function se = se(vector)
    n = numel(vector);                % Number of data points
    sampleMean = mean(vector);        % Sample mean
    sampleStdDev = std(vector);       % Sample standard deviation
    se = sampleStdDev / sqrt(n);      % Standard error
end