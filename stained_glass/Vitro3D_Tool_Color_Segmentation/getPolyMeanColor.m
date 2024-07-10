function [mean_R,mean_G,mean_B] = getPolyMeanColor(R,mask)

mask_logical = logical(mask);

masked_R = R(:,:,1) .* mask_logical;
masked_G = R(:,:,2) .* mask_logical;
masked_B = R(:,:,3) .* mask_logical;

% Calculate the mean of the non-zero values in each channel
mean_R = mean(masked_R(masked_R > 0));
mean_G = mean(masked_G(masked_G > 0));
mean_B = mean(masked_B(masked_B > 0));

if isnan(mean_R)
    mean_R = 0;
end
if isnan(mean_G)
    mean_G = 0;
end
if isnan(mean_B)
    mean_B = 0;
end

end % function