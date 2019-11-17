DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS Canvas;
DROP TABLE IF EXISTS Landmark;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS sex;
-- REF TABLES
CREATE TABLE IF NOT EXISTS `sex` (
  `sexID` INT(1),
  `value` VARCHAR(255),
  PRIMARY KEY `pk_sexID`(`sexID`)
);
INSERT INTO `sex`
SET
  `sexID` = 0,
  `value` = "Not Known";
INSERT INTO `sex`
SET
  `sexID` = 1,
  `value` = "Male";
INSERT INTO `sex`
SET
  `sexID` = 2,
  `value` = "Female";
INSERT INTO `sex`
SET
  `sexID` = 9,
  `value` = "N.A.";
-- ACTUAL TABLES
  CREATE TABLE user (
    `userID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `password` VARCHAR(64) NOT NULL,
    `salt` VARCHAR(25),
    `name` VARCHAR(50) DEFAULT "",
    `age` INT(3) DEFAULT -1,
    -- ISO/IEC 5218: 0 = "Not Known", 1 = "male", 2 = "female", 9 = "N.A."
    `sex` INT(1) DEFAULT 0,
    `commute_method` INT(2) DEFAULT 0,
    `active` BOOLEAN DEFAULT 1,
    `token` VARCHAR(64),
    CONSTRAINT User_userID_PK PRIMARY KEY(userID),
    CONSTRAINT User_email_UQ UNIQUE INDEX(email),
    -- RefTables
    CONSTRAINT User_sex_FK FOREIGN KEY(sex) REFERENCES sex(sexID)
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
CREATE TABLE comment (
    `commentID` INT(8) UNSIGNED AUTO_INCREMENT NOT NULL,
    `userID` INT(8) UNSIGNED,
    `canvasID` INT(8) UNSIGNED,
    `text` VARCHAR(140),
    `timestamp` DATETIME,
    `active` BOOLEAN DEFAULT 1,
    CONSTRAINT Comment_commentID_PK PRIMARY KEY(commentID),
    CONSTRAINT Comment_userID_FK FOREIGN KEY(userID) REFERENCES User(userID),
    CONSTRAINT Comment_canvasID_FK FOREIGN KEY(canvasID) REFERENCES Canvas(canvasID)
  );