CREATE OR REPLACE VIEW activeUsers AS
SELECT
  `userID`,
  `email`,
  `name`,
  `age`,
  `S`.`value` as 'sex',
  `commute_method`
FROM user U
join sex S ON U.sex = S.sexID
WHERE
  `active` = True