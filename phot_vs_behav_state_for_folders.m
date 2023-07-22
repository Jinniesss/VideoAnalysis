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
% figure(1);
% set(gcf, 'Position', [100, 100, 1200, 400]);
% mean1 = mean(in_loco_all);
% mean2 = mean(in_nonl_all);
% mean3 = mean(in_immo_all);
% sd1 = se(in_loco_all);
% sd2 = se(in_nonl_all);
% sd3 = se(in_immo_all);
% 
% ax2 = subplot(1,3,1);
% hold(ax2, 'on');
% bar(ax2, [1, 2,3], [mean1, mean2,mean3]);
% hold(ax2, 'off');
% 
% % Plot error bars for standard deviation
% hold(ax2, 'on');
% errorbar(ax2, [1, 2,3], [mean1, mean2,mean3], [sd1, sd2,sd3], '.', 'LineWidth', 1);
% hold(ax2, 'off');
% 
% % Customize the plot
% ylabel('Photometry');
% xticks(ax2, [1,2,3]);
% xticklabels(ax2, {'Locomotion', 'Non-locomotor','Immobility'});
% grid(ax2, 'off');
% title('In Nest')
% % saveas(gcf, [name '_phot_in_nest.png']);
% 
% %% Out of nest -- phot v.s. mov_states
% mean1 = mean(out_loco_all);
% mean2 = mean(out_nonl_all);
% mean3 = mean(out_immo_all);
% sd1 = se(out_loco_all);
% sd2 = se(out_nonl_all);
% sd3 = se(out_immo_all);
% 
% ax1 = subplot(1,3,2);
% hold(ax1, 'on');
% bar(ax1, [1, 2,3], [mean1, mean2, mean3]);
% hold(ax1, 'off');
% 
% % Plot error bars for standard deviation
% hold(ax1, 'on');
% errorbar(ax1, [1, 2,3], [mean1, mean2, mean3], [sd1, sd2, sd3], '.', 'LineWidth', 1);
% hold(ax1, 'off');
% 
% % Customize the plot
% ylabel('Photometry');
% xticks(ax1, [1, 2, 3]);
% xticklabels(ax1, {'Locomotion', 'Non-locomotor','Immobility'});
% grid(ax1, 'off');
% title('Out of Nest');
% 
% %% 
% subplot(1,3,3)
% t_loco_w = length(in_loco_w_all) + length(out_loco_w_all);
% t_nonl_w = length(in_nonl_w_all) + length(out_nonl_w_all);
% t_immo_w = length(in_immo_w_all) + length(out_immo_w_all);
% time_w = horzcat(t_loco_w,t_nonl_w,t_immo_w);
% time_w = time_w/sum(time_w);
% bar(time_w);
% ylabel('percentage');
% title('Time of behavioral states during Wakefulness');
% xticks(1:3);
% xticklabels({'Locomotion', 'Non-locomotor', 'Immobility'});







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