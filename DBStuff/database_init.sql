DROP TABLE IF EXISTS canvas_rating;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS canvas;
DROP TABLE IF EXISTS landmark;
DROP TABLE IF EXISTS user;
-- ACTUAL TABLES
CREATE TABLE user (
  `userID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(64) NOT NULL,
  `salt` VARCHAR(25),
  `name` VARCHAR(50) DEFAULT "",
  `birthdate` VARCHAR(30) DEFAULT "1970-01-01T00:00:00Z",
  `sex` VARCHAR(15) DEFAULT "Not Known",
  `commute_method` VARCHAR(15) DEFAULT "",
  `active` BOOLEAN DEFAULT 1,
  `token` VARCHAR(64),
  `temp_token` VARCHAR(64),
  CONSTRAINT User_userID_PK PRIMARY KEY(userID),
  CONSTRAINT User_email_UQ UNIQUE INDEX(email)
);
CREATE TABLE landmark (
  -- From GOOGLE API
  `placeID` VARCHAR(30),
  `name` VARCHAR(20),
  `description` VARCHAR(280),
  `active` BOOLEAN DEFAULT 1,
  CONSTRAINT Landmark_placeID_PK PRIMARY KEY(placeID)
);
CREATE TABLE canvas (
  `canvasID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
  `userID` INT(8) UNSIGNED,
  `placeID` VARCHAR(30),
  `title` VARCHAR(25),
  `description` VARCHAR(140),
  `editable` BOOLEAN,
  `active` BOOLEAN DEFAULT 1,
  CONSTRAINT Canvas_canvasID_PK PRIMARY KEY(canvasID),
  CONSTRAINT Canvas_userID_FK FOREIGN KEY(userID) REFERENCES User(userID),
  CONSTRAINT Canvas_placeID_FK FOREIGN KEY(placeID) REFERENCES Landmark(placeID)
);
CREATE TABLE canvas_rating (
  `canvas_ratingID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
  `canvasID` INT(8) UNSIGNED NOT NULL,
  `userID` INT(8) UNSIGNED NOT NULL,
  CONSTRAINT Canvas_Rating_canvas_ratingID_PK PRIMARY KEY(canvas_ratingID),
  CONSTRAINT Canvas_Rating_userID_FK FOREIGN KEY(userID) REFERENCES User(userID),
  CONSTRAINT Canvas_Rating_canvasID_FK FOREIGN KEY(canvasID) REFERENCES Canvas(canvasID)
);
CREATE TABLE comment (
  `commentID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
  `userID` INT(8) UNSIGNED,
  `canvasID` INT(8) UNSIGNED,
  `text` VARCHAR(140),
  `timestamp` VARCHAR(30) DEFAULT "1970-01-01T00:00:00Z",
  `active` BOOLEAN DEFAULT 1,
  CONSTRAINT Comment_commentID_PK PRIMARY KEY(commentID),
  CONSTRAINT Comment_userID_FK FOREIGN KEY(userID) REFERENCES User(userID),
  CONSTRAINT Comment_canvasID_FK FOREIGN KEY(canvasID) REFERENCES Canvas(canvasID)
);