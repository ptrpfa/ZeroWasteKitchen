-- MySQL dump 10.13  Distrib 8.0.33, for macos13.3 (arm64)
--
-- Host: localhost    Database: RecipeDB
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `RecipeDB`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `RecipeDB` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `RecipeDB`;

--
-- Table structure for table `DietRestriction`
--

DROP TABLE IF EXISTS `DietRestriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DietRestriction` (
  `RestrictionID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` varchar(500) NOT NULL DEFAULT '',
  PRIMARY KEY (`RestrictionID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DietRestriction`
--

LOCK TABLES `DietRestriction` WRITE;
/*!40000 ALTER TABLE `DietRestriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `DietRestriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Ingredient`
--

DROP TABLE IF EXISTS `Ingredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Ingredient` (
  `IngredientID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Type` varchar(100) NOT NULL DEFAULT 'General',
  PRIMARY KEY (`IngredientID`),
  UNIQUE KEY `Ingredient_UN_Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Ingredient`
--

LOCK TABLES `Ingredient` WRITE;
/*!40000 ALTER TABLE `Ingredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `Ingredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Recipe`
--

DROP TABLE IF EXISTS `Recipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Recipe` (
  `RecipeID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `MealType` varchar(100) NOT NULL DEFAULT 'General',
  `Cuisine` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`RecipeID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Recipe`
--

LOCK TABLES `Recipe` WRITE;
/*!40000 ALTER TABLE `Recipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `Recipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RecipeDietRestriction`
--

DROP TABLE IF EXISTS `RecipeDietRestriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RecipeDietRestriction` (
  `MappingID` int NOT NULL AUTO_INCREMENT,
  `RecipeID` int NOT NULL,
  `RestrictionID` int NOT NULL,
  PRIMARY KEY (`MappingID`),
  KEY `RecipeDietRestriction_FK_Recipe` (`RecipeID`),
  KEY `RecipeDietRestriction_FK_DietRestriction` (`RestrictionID`),
  CONSTRAINT `RecipeDietRestriction_FK_DietRestriction` FOREIGN KEY (`RestrictionID`) REFERENCES `DietRestriction` (`RestrictionID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `RecipeDietRestriction_FK_Recipe` FOREIGN KEY (`RecipeID`) REFERENCES `Recipe` (`RecipeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RecipeDietRestriction`
--

LOCK TABLES `RecipeDietRestriction` WRITE;
/*!40000 ALTER TABLE `RecipeDietRestriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `RecipeDietRestriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RecipeIngredient`
--

DROP TABLE IF EXISTS `RecipeIngredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RecipeIngredient` (
  `MappingID` int NOT NULL AUTO_INCREMENT,
  `RecipeID` int NOT NULL,
  `IngredientID` int NOT NULL,
  `Quantity` float NOT NULL DEFAULT '0',
  `Measurement` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`MappingID`),
  KEY `RecipeIngredient_FK_Recipe` (`RecipeID`),
  KEY `RecipeIngredient_FK_Ingredient` (`IngredientID`),
  CONSTRAINT `RecipeIngredient_FK_Ingredient` FOREIGN KEY (`IngredientID`) REFERENCES `Ingredient` (`IngredientID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `RecipeIngredient_FK_Recipe` FOREIGN KEY (`RecipeID`) REFERENCES `Recipe` (`RecipeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RecipeIngredient`
--

LOCK TABLES `RecipeIngredient` WRITE;
/*!40000 ALTER TABLE `RecipeIngredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `RecipeIngredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(100) NOT NULL,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL DEFAULT '',
  `Email` varchar(100) NOT NULL,
  `Password` varchar(100) NOT NULL DEFAULT '',
  `DOB` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `User_UN_Username` (`Username`),
  UNIQUE KEY `User_UN_Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User`
--

LOCK TABLES `User` WRITE;
/*!40000 ALTER TABLE `User` DISABLE KEYS */;
/*!40000 ALTER TABLE `User` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserDietRestriction`
--

DROP TABLE IF EXISTS `UserDietRestriction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserDietRestriction` (
  `MappingID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `RestrictionID` int NOT NULL,
  PRIMARY KEY (`MappingID`),
  KEY `UserDietRestriction_FK_User` (`UserID`),
  KEY `UserDietRestriction_FK_DietRestriction` (`RestrictionID`),
  CONSTRAINT `UserDietRestriction_FK_DietRestriction` FOREIGN KEY (`RestrictionID`) REFERENCES `DietRestriction` (`RestrictionID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `UserDietRestriction_FK_User` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserDietRestriction`
--

LOCK TABLES `UserDietRestriction` WRITE;
/*!40000 ALTER TABLE `UserDietRestriction` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserDietRestriction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UserRecipe`
--

DROP TABLE IF EXISTS `UserRecipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `UserRecipe` (
  `MappingID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `RecipeID` int NOT NULL,
  `Datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`MappingID`),
  KEY `UserRecipe_FK_User` (`UserID`),
  KEY `UserRecipe_FK_Recipe` (`RecipeID`),
  CONSTRAINT `UserRecipe_FK_Recipe` FOREIGN KEY (`RecipeID`) REFERENCES `Recipe` (`RecipeID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `UserRecipe_FK_User` FOREIGN KEY (`UserID`) REFERENCES `User` (`UserID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `UserRecipe`
--

LOCK TABLES `UserRecipe` WRITE;
/*!40000 ALTER TABLE `UserRecipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `UserRecipe` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-13 15:22:15
