CREATE
OR REPLACE VIEW activeUsers AS
SELECT
  `userID`,
  `name`,
  `birthdate`,
  `sex`,
  `commute_method`
FROM user
WHERE
  `active` = True;
CREATE
  OR REPLACE VIEW activeLandmarks AS
SELECT
  `placeID`,
  `name`,
  `description`
FROM `landmark`
WHERE
  `active` = True;
CREATE
  OR REPLACE VIEW activeCanvases AS
SELECT
  `canvasID`,
  `userID`,
  `placeID`,
  `title`,
  `description`,
  `editable`
FROM canvas
WHERE
  `active` = True;
CREATE
  OR REPLACE VIEW activeComments AS
SELECT
  `commentID`,
  `userID`,
  `canvasID`,
  `text`,
  `timestamp`
FROM comment
WHERE
  `active` = True;
CREATE
  OR REPLACE VIEW countRating AS
SELECT
  canvasID,
  COUNT(canvas_ratingID) AS rating
FROM canvas_rating
WHERE
  liked = 1
GROUP BY canvasID;