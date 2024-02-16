function [newPoints] = scaleTile(tilePoints, scaleFactorX, scaleFactorY)
    % Scale tiles and keep 
    scaleFactors = [scaleFactorX, scaleFactorY];
    
    % Calculate centroid
    centroid = mean(tilePoints);
    translatedPoints = tilePoints - centroid;
    
    scalingMatrix = diag(scaleFactors);
    scaledTranslatedPoints = translatedPoints * scalingMatrix;
    
    newPoints = scaledTranslatedPoints + centroid;
end