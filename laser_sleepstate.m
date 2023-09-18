load('labels.mat')
load('laser_real/laser.mat')
labels = labels.';

labels_len = length(labels);
labels_diff = diff(labels);
labels_change = find(labels_diff ~= 0);     % index of 5s-bouts
labels_change = horzcat(labels_change,labels_len-1);  

labels_time = % to be complete HERE

labels_change_sec = labels_time(labels_change)*3600;  % index of seconds
labels_change_sec(end) = labels_change_sec(end) + 5;    % 5--bout length of labels
cur_label = zeros(labels_len,1);
for i = 1:length(labels)
    label_idx = labels_change(find(labels_change_sec>=labels(i),1));
    if isempty(label_idx)
        continue;
    end
    cur_label(i) = labels(label_idx);

end