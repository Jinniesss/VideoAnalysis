clear;

path = pwd;
folders = dir(path);
folders = folders([folders.isdir]);  % Filter out non-folders

phot_beh_sum = [];
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

    df_path = [folder '_phot_vs_beh.mat'];
    if ~exist(df_path, 'file')
        phot_vs_behav_state();
    end
    df = load(df_path);
    data = df.phot_behv;
    phot_beh_sum = vertcat(phot_beh_sum,data);

    if flag
        m = get_mousename(folder);
        flag=false;
    end
    cd(path);
end

phot_beh_sum.session = sessions;

save([m '_phot_beh_summary.mat'],"phot_beh_sum")

%% In nest -- phot v.s. mov_states
close all;
figure(1);
set(gcf, 'Position', [100, 100, 1200, 400]);
mean1 = mean(phot_beh_sum.in_LM);
mean2 = mean(phot_beh_sum.in_NL);
mean3 = mean(phot_beh_sum.in_QW);
mean4 = mean(phot_beh_sum.in_NREM);
mean5 = mean(phot_beh_sum.in_REM);
sd1 = se(phot_beh_sum.in_LM);
sd2 = se(phot_beh_sum.in_NL);
sd3 = se(phot_beh_sum.in_QW);
sd4 = se(phot_beh_sum.in_NREM);
sd5 = se(phot_beh_sum.in_REM);

ax2 = subplot(1,3,1);
hold(ax2, 'on');
bar(ax2, [1, 2,3,4,5], [mean1, mean2,mean3,mean4,mean5]);
hold(ax2, 'off');

% Plot error bars for standard deviation
hold(ax2, 'on');
errorbar(ax2, [1, 2,3,4,5], [mean1, mean2,mean3,mean4,mean5], [sd1, sd2,sd3,sd4,sd5], '.', 'LineWidth', 1);
hold(ax2, 'off');

% Customize the plot
ylabel('Photometry');
xticks(ax2, [1,2,3,4,5]);
xticklabels(ax2, {'Locomotion', 'Non-locomotor','Quiet Wakefulness','NREM','REM'});
grid(ax2, 'off');
title('In Nest')
% saveas(gcf, [name '_phot_in_nest.png']);

%% Out of nest -- phot v.s. mov_states
mean1 = mean(phot_beh_sum.out_LM);
mean2 = mean(phot_beh_sum.out_NL);
mean3 = mean(phot_beh_sum.out_QW);
mean4 = mean(phot_beh_sum.out_NREM);
mean5 = mean(phot_beh_sum.out_REM);
sd1 = se(phot_beh_sum.out_LM);
sd2 = se(phot_beh_sum.out_NL);
sd3 = se(phot_beh_sum.out_QW);
sd4 = se(phot_beh_sum.out_NREM);
sd5 = se(phot_beh_sum.out_REM);

ax1 = subplot(1,3,2);
hold(ax1, 'on');
bar(ax1, [1, 2,3,4,5], [mean1, mean2, mean3,mean4,mean5]);
hold(ax1, 'off');

% Plot error bars for standard deviation
hold(ax1, 'on');
errorbar(ax1, [1, 2,3,4,5], [mean1, mean2,mean3,mean4,mean5], [sd1, sd2,sd3,sd4,sd5], '.', 'LineWidth', 1);
hold(ax1, 'off');

% Customize the plot
ylabel('Photometry');
xticks(ax1, [1, 2, 3,4,5]);
xticklabels(ax1, {'Locomotion', 'Non-locomotor','Quiet Wakefulness','NREM','REM'});
grid(ax1, 'off');
title('Out of Nest');

%% 
ax3 = subplot(1,3,3);
mean1 = mean(phot_beh_sum.t_LM);
mean2 = mean(phot_beh_sum.t_NL);
mean3 = mean(phot_beh_sum.t_QW);
sd1 = se(phot_beh_sum.t_LM);
sd2 = se(phot_beh_sum.t_NL);
sd3 = se(phot_beh_sum.t_QW);
hold(ax3, 'on');
bar(ax3,[1,2,3],[mean1,mean2,mean3]);
errorbar(ax3,[1,2,3],[mean1, mean2,mean3], [sd1, sd2,sd3], '.', 'LineWidth', 1);
ylabel('Time(hour)');
title('Time of behavioral states during Wakefulness');
xticks(1:3);
xticklabels({'Locomotion', 'Non-locomotor', 'Quiet Wakefulness'});

saveas(gcf, [m '_phot_vs_behv.png']);





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