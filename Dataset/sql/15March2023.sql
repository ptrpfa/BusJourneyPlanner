-- MySQL dump 10.13  Distrib 8.0.32, for macos13.0 (arm64)
--
-- Host: localhost    Database: DSA_JP
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
-- Current Database: `DSA_JP`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `DSA_JP` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `DSA_JP`;

--
-- Table structure for table `Bus`
--

DROP TABLE IF EXISTS `Bus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bus` (
  `BusID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Type` int NOT NULL DEFAULT '1',
  `StartBusStopID` int unsigned NOT NULL,
  `EndBusStopID` int unsigned NOT NULL,
  PRIMARY KEY (`BusID`),
  UNIQUE KEY `Bus_UN` (`Name`),
  UNIQUE KEY `Bus_UN2` (`BusID`),
  KEY `Bus_FK` (`StartBusStopID`),
  KEY `Bus_FK_1` (`EndBusStopID`),
  CONSTRAINT `Bus_FK` FOREIGN KEY (`StartBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Bus_FK_1` FOREIGN KEY (`EndBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bus`
--

LOCK TABLES `Bus` WRITE;
/*!40000 ALTER TABLE `Bus` DISABLE KEYS */;
INSERT INTO `Bus` VALUES (1,'P101',2,1,1),(2,'P106',2,19,19),(3,'P202',2,49,49),(4,'P403',2,75,75),(5,'P102-01',1,19,11),(6,'P102-02',1,11,19),(7,'P211-01',1,49,1),(8,'P211-02',1,1,49),(9,'P411-01',1,135,1),(10,'P411-02',1,1,135);
/*!40000 ALTER TABLE `Bus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BusRoute`
--

DROP TABLE IF EXISTS `BusRoute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BusRoute` (
  `RouteID` int unsigned NOT NULL AUTO_INCREMENT,
  `BusID` int unsigned NOT NULL,
  `BusStopID` int unsigned NOT NULL,
  `StopOrder` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`RouteID`),
  UNIQUE KEY `BusRoute_UN` (`RouteID`),
  KEY `BusRoute_FK` (`BusID`),
  KEY `BusRoute_FK_1` (`BusStopID`),
  CONSTRAINT `BusRoute_FK` FOREIGN KEY (`BusID`) REFERENCES `Bus` (`BusID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `BusRoute_FK_1` FOREIGN KEY (`BusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=241 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BusRoute`
--

LOCK TABLES `BusRoute` WRITE;
/*!40000 ALTER TABLE `BusRoute` DISABLE KEYS */;
INSERT INTO `BusRoute` VALUES (1,1,1,-1),(2,1,2,1),(3,1,3,2),(4,1,4,3),(5,1,5,4),(6,1,6,5),(7,1,7,6),(8,1,8,7),(9,1,9,8),(10,1,10,9),(11,1,11,10),(12,1,12,11),(13,1,13,12),(14,1,14,13),(15,1,15,14),(16,1,16,15),(17,1,17,16),(18,1,18,17),(19,2,19,-1),(20,2,20,1),(21,2,21,2),(22,2,46,3),(23,2,23,4),(24,2,24,5),(25,2,25,6),(26,2,26,7),(27,2,27,8),(28,2,28,9),(29,2,29,10),(30,2,30,11),(31,2,31,12),(32,2,32,13),(33,2,33,14),(34,2,34,15),(35,2,35,16),(36,2,36,17),(37,2,37,18),(38,2,39,19),(39,2,39,20),(40,2,40,21),(41,2,27,22),(42,2,26,23),(43,2,41,24),(44,2,42,25),(45,2,43,26),(46,2,44,27),(47,2,45,28),(48,2,46,29),(49,2,47,30),(50,2,48,31),(51,2,19,32),(52,3,49,-1),(53,3,50,1),(54,3,51,2),(55,3,52,3),(56,3,53,4),(57,3,54,5),(58,3,55,6),(59,3,56,7),(60,3,57,8),(61,3,58,9),(62,3,59,10),(63,3,60,11),(64,3,61,12),(65,3,62,13),(66,3,63,14),(67,3,64,15),(68,3,65,16),(69,3,66,17),(70,3,67,18),(71,3,68,19),(72,3,69,20),(73,3,70,21),(74,3,71,22),(75,3,72,23),(76,3,73,24),(77,3,50,25),(78,3,74,26),(79,4,75,-1),(80,4,76,1),(81,4,77,2),(82,4,78,3),(83,4,79,4),(84,4,80,5),(85,4,77,6),(86,4,81,7),(87,4,91,8),(88,4,83,9),(89,4,84,10),(90,4,85,11),(91,4,86,12),(92,4,87,13),(93,4,64,14),(94,4,65,15),(95,4,66,16),(96,4,67,17),(97,4,88,18),(98,4,89,19),(99,4,90,20),(100,4,91,21),(101,4,92,22),(102,5,19,1),(103,5,93,2),(104,5,94,3),(105,5,95,4),(106,5,96,5),(107,5,97,6),(108,5,98,7),(109,5,99,8),(110,5,11,9),(111,6,11,1),(112,6,12,2),(113,6,13,3),(114,6,98,4),(115,6,97,5),(116,6,100,6),(117,6,101,7),(118,6,20,8),(119,6,21,9),(120,6,48,10),(121,6,19,11),(122,6,19,12),(123,7,49,1),(124,7,134,2),(125,7,103,3),(126,7,104,4),(127,7,105,5),(128,7,106,6),(129,7,107,7),(130,7,108,8),(131,7,109,9),(132,7,86,10),(133,7,87,11),(134,7,110,12),(135,7,111,13),(136,7,129,14),(137,7,112,15),(138,7,113,16),(139,7,114,17),(140,7,115,18),(141,7,116,19),(142,7,117,20),(143,7,118,21),(144,7,119,22),(145,7,120,23),(146,7,121,24),(147,7,1,25),(148,8,1,1),(149,8,2,2),(150,8,122,3),(151,8,120,4),(152,8,123,5),(153,8,124,6),(154,8,125,7),(155,8,126,8),(156,8,127,9),(157,8,128,10),(158,8,129,11),(159,8,130,12),(160,8,110,13),(161,8,64,14),(162,8,65,15),(163,8,66,16),(164,8,67,17),(165,8,131,18),(166,8,70,19),(167,8,103,20),(168,8,104,21),(169,8,105,22),(170,8,106,23),(171,8,107,24),(172,8,132,25),(173,8,133,26),(174,8,134,27),(175,8,49,28),(176,9,135,1),(177,9,136,2),(178,9,137,3),(179,9,138,4),(180,9,139,5),(181,9,140,6),(182,9,141,7),(183,9,142,8),(184,9,143,9),(185,9,144,10),(186,9,91,11),(187,9,83,12),(188,9,84,13),(189,9,85,14),(190,9,86,15),(191,9,87,16),(192,9,110,17),(193,9,111,18),(194,9,129,19),(195,9,112,20),(196,9,113,21),(197,9,114,22),(198,9,115,23),(199,9,116,24),(200,9,117,25),(201,9,118,26),(202,9,119,27),(203,9,120,28),(204,9,121,29),(205,9,1,30),(206,10,1,1),(207,10,2,2),(208,10,122,3),(209,10,120,4),(210,10,123,5),(211,10,124,6),(212,10,125,7),(213,10,126,8),(214,10,127,9),(215,10,128,10),(216,10,129,11),(217,10,130,12),(218,10,110,13),(219,10,64,14),(220,10,65,15),(221,10,66,16),(222,10,67,17),(223,10,88,18),(224,10,89,19),(225,10,90,20),(226,10,91,21),(227,10,145,22),(228,10,146,23),(229,10,144,24),(230,10,147,25),(231,10,142,26),(232,10,148,27),(233,10,149,28),(234,10,150,29),(235,10,151,30),(236,10,152,31),(237,10,153,32),(238,10,137,33),(239,10,154,34),(240,10,135,35);
/*!40000 ALTER TABLE `BusRoute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BusStop`
--

DROP TABLE IF EXISTS `BusStop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BusStop` (
  `BusStopID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(500) NOT NULL,
  `Latitude` double NOT NULL,
  `Longitude` double NOT NULL,
  PRIMARY KEY (`BusStopID`),
  UNIQUE KEY `BusStop_UN` (`Name`),
  UNIQUE KEY `BusStop_UN2` (`BusStopID`)
) ENGINE=InnoDB AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BusStop`
--

LOCK TABLES `BusStop` WRITE;
/*!40000 ALTER TABLE `BusStop` DISABLE KEYS */;
INSERT INTO `BusStop` VALUES (1,'Larkin Terminal',1.4964559999542668,103.74374661113058),(2,'Pejabat Daerah Tanah Johor Bahru',1.491850778809332,103.74087255093272),(3,'RTM Jabatan Penyiaran Negeri Johor',1.4801823177394162,103.7368168221016),(4,'Opp Masjid Kolam Ayer',1.4689940555974177,103.7368740086021),(5,'Opp Jabatan Pendidikan Johor',1.4675510557185905,103.73673088953657),(6,'Maktab Sultan Abu Bakar (English College',1.4627466510403129,103.73965194475493),(7,'Hospital Sultanah Aminah',1.4575742843315376,103.74670675307506),(8,'Johor Islamic Complex',1.456742090233385,103.74938268472616),(9,'Bangunan Sultan Ibrahim',1.4598336266506124,103.76216068221784),(10,'Wisma Persekutuan',1.4609620562865593,103.75782511045665),(11,'Majlis Bandaraya Johor Bahru',1.4555985388016415,103.76176881099856),(12,'JB Sentral Terminal',1.4635691591027955,103.76499694129318),(13,'Menara MSC Cyberport',1.4622515143439279,103.77198033612271),(14,'Opp Sekolah Kebangsaan Perempuan Jalan Yahya Awal',1.4728712972429236,103.74885185047674),(15,'Petronas Kiosk @ Jalan Yahya Awal',1.4753718119884702,103.7479248341084),(16,'Opp SJK (T) Jalan Yahya Awal',1.478736856876273,103.74753116069688),(17,'aft Jalan Tasek Utara',1.4810361535128787,103.74738498637815),(18,'Opp Yayasan Bandaraya Johor Bahru',1.4843491421227393,103.74925303801986),(19,'Hub PPR Sri Stulang',1.495066778509724,103.78766489813552),(20,'aft Jalan Pasir Pelangi',1.4961999552580305,103.7842123533323),(21,'Petronas Kiosk @ Taman Bayu Puteri',1.4971903071581996,103.78956720733493),(22,'BHPetrol Kiosk @ Permas Jaya',1.4942010877822336,103.81293468220896),(23,'AEON Permas Jaya',1.4960852287704014,103.81969568579773),(24,'Dewan Serbaguna Permas Jaya',1.4977243949059944,103.82415696808461),(25,'Mon Glori Apartment',1.500135152236701,103.82219739383686),(26,'Opp Best Ku Motor',1.5210770997516314,103.820602817106),(27,'Opp Kia Motors',1.5263136695996888,103.81667548941742),(28,'bef Jalan Masai Baru',1.5234081864988613,103.81300609325264),(29,'Lotus Plentong (Tesco Extra)',1.5208503941324885,103.81512393616983),(30,'aft Jalan Masai Baru',1.5233928073879512,103.81260417664944),(31,'Giant Plentong',1.5278964005623548,103.81601426255317),(32,'Hse No. 1 Jalan Seroja 22',1.5310476061988132,103.8145170588567),(33,'Opp Jalan Keembong 43',1.5333407999575837,103.80570189815187),(34,'Jalan Seroja 54',1.5370755247775638,103.79990688093852),(35,'Jalan Bakawali 86',1.5383792496951987,103.79904754232605),(36,'Opp Pasar Awam Johor Jaya',1.5442854061651363,103.79952183431531),(37,'AEON Tebrau City',1.551607288125913,103.79669251653316),(38,'Hospital Sultan Ismail',1.5499616635265265,103.7903773386306),(39,'Hospital Sultan Ismail 2',1.5461347994301888,103.78920168581082),(40,'Opp Suntoyo Enterprise',1.5341435435769857,103.80433427473359),(41,'House No. 63 Jalan Permas 1/1',1.5148264261333237,103.81827810186249),(42,'Jalan Permas 5/6',1.5038237251409665,103.8176464576763),(43,'Sekolah Kebangsaan Taman Permas Jaya 3',1.5001862028022683,103.8204708549044),(44,'Pan Vista',1.5001335277464176,103.82219863061796),(45,'aft Jalan Permas 8/14',1.5001599109500323,103.82588336441847),(46,'Opp BHPetrol Kiosk @ Permas Jaya',1.4938852204096618,103.81312044545798),(47,'bef Shell Kiosk @ Permas Jaya',1.4923948683016146,103.80490543187601),(48,'Opp Petronas Kiosk @ Taman Bayu Puteri',1.4968842607355726,103.78946726500905),(49,'Taman Universiti Terminal',1.5386151368910133,103.62871889454172),(50,'opp Sekolah Kebangsaan Taman Universiti 4',1.534308506240654,103.62710937673535),(51,'Surau As Syakirin',1.5300540567469194,103.62919660110482),(52,'Opp SMK Taman Mutiara Rini',1.5245751999325976,103.63517558879529),(53,'Opp Jalan Utama 34',1.5209523625266286,103.6382563336594),(54,'Opp Hutan Bandar MBIP',1.511956346715004,103.63465643183984),(55,'Shop No. 81 Jalan Seri Orkid 17',1.5101921953830588,103.64217620731986),(56,'Opp Bahagian Teknologi Pendidikan Negeri Johor',1.5175625167281073,103.64918489637948),(57,'Union Inn',1.5158966494768213,103.65719490175148),(58,'Shophouses @ Jalan Nakhoda 2',1.51794055733978,103.65911972380891),(59,'bef Terminal TUTA',1.5197638759318781,103.66085007960669),(60,'Polilkinik Yap',1.5225300824672,103.66338557173337),(61,'bef Jalan Tun Teja',1.5243236689609123,103.66502786371659),(62,'Shophouses @ Jalan Perwira 9',1.5276000687198807,103.66490681659525),(63,'Sin Kok Soon Motor (JB) Sdn Bhd',1.5295849000522657,103.66525083069143),(64,'aft Jalan Patin',1.5350511809872578,103.66474654589447),(65,'SJK(C) Pu Sze',1.5365257998200346,103.66343750790784),(66,'aft Shell Kiosk - Skudai',1.5397247249617794,103.66050127115842),(67,'Shell Kiosk @ Taman Sri Putri',1.5449034370227417,103.65727484903925),(68,'Masjid Abidin',1.5429731311255839,103.65085627727618),(69,'Shophouses along Jalan Tembaga Kuning 4',1.544925677392113,103.6527194257566),(70,'Shophouses @ Jalan Suasa 1',1.549647043669743,103.65179955454633),(71,'bef Jalan Hamoni 14',1.5445769961776104,103.64397333250112),(72,'Opp Apartment Pasti Asli',1.5412268239025178,103.6412379663487),(73,'Opp Surau As Syakirin',1.5297380248680652,103.62928263558307),(74,'Jalan Kebudayaan 27 / 24 Intersection',1.535736987403005,103.6281658048895),(75,'Econsave Senai',1.6110068446478472,103.65629332000914),(76,'Opp Pusat Hemodialisis Rotary Kulai',1.6125013180073793,103.65816892145304),(77,'Opp Taman Bintang',1.6145424343173105,103.658532012215),(78,'Kawasan Perindustrian Senai 3',1.6261343968296889,103.65631508831991),(79,'Senai Airport Terminal',1.6349379250179437,103.66630691168017),(80,'NSTP Senai',1.6283976940465283,103.65689819511196),(81,'Taman Mewah',1.6093409706514916,103.65682082209246),(82,'Medan Selera Senai',1.6013846087875712,103.64515677546767),(83,'Opp Sekolah Kebangsaan Senai',1.596764420712483,103.64559102580564),(84,'Opp BHPetrol Kiosk @ Taman Aman',1.5910215647537664,103.64796686012346),(85,'aft Lebuhraya Utara-Selatan',1.5710682887829601,103.66094006994001),(86,'Opp Shell Kiosk @ Taman Sri Putri',1.5446071130881212,103.65778209077513),(87,'Skudai Parade',1.541540224027169,103.65954500502208),(88,'aft Tenaga Nasional Bhd Substation',1.554106991277451,103.65853254841942),(89,'bef BHPetrol Kiosk @ Taman Aman',1.5906962752714202,103.64770108827454),(90,'bef Sekolah Kebangsaan Senai',1.595899319482502,103.64536899139767),(91,'Opp Medan Selera Senai',1.6002634055808034,103.64459319263067),(92,'bef Econsave @ Senai',1.6102010601670786,103.65715287633772),(93,'bef Jalan Sultanah Aminah',1.4918540438972152,103.78522939384607),(94,'Shell Kiosk @ Jalan Pasir Pelangi',1.490657221092022,103.7858710502786),(95,'Stulang Walk',1.473219175868682,103.77987903309756),(96,'Block 18',1.4712543517887378,103.78119274105374),(97,'Opp De\' Stulang',1.4694586265386058,103.7816131693062),(98,'Opp Sekolah Menengah Foon Yew',1.4670599696628617,103.77888348421564),(99,'R&F Mall',1.4604109500292848,103.76940139190562),(100,'Opp Istana Pasir Pelangi',1.47802564822168,103.78087113857356),(101,'The Mall, Mid Valley Southkey',1.5005936801337696,103.77679017331387),(102,'Aeon Taman Universiti',1.5423777121603113,103.62969894227055),(103,'UTM Fakulti Alam Bina',1.5598595502801802,103.63478382209261),(104,'Opp Block D10',1.5627697345949043,103.63645243799397),(105,'Opp C.I.C.T.',1.5627095018015627,103.63914999722523),(106,'Block P07 - Fakulti Kejuruteraan Elektrik',1.5604593962896607,103.64164333508509),(107,'aft Block P19A - Fakulti Kejuruteraan Elektrik',1.558167973564592,103.64021955093295),(108,'UTM Equine Park',1.5553378482590166,103.6410112229101),(109,'UTM Rumah Alumni',1.5533050263979893,103.6427117938282),(110,'Opp SJK (C) Kuo Kuang',1.528201281584724,103.67097274711804),(111,'bef Paradigm Mall',1.51926239182888,103.68206611709597),(112,'Opp Saksama Otomobil',1.5121383386574008,103.68706591589486),(113,'Opp Petron Kiosk @ Taman Tampoi Indah',1.5088584686178155,103.68928902381539),(114,'Kompleks Pekan Rabu Johor Bahru',1.5008855908671468,103.69599314953071),(115,'Giant Tampoi',1.498877450327011,103.69886295948693),(116,'aft Lorong Betik',1.4969289341746932,103.70179963586516),(117,'Batu 5 Johor Street Market',1.4957308782478185,103.70353570332152),(118,'Plaza Angsana',1.494173589831715,103.70574439346098),(119,'Klinik Utama @ Jalan Padi 1',1.489587186962772,103.71219076437811),(120,'Opp Amitabha Centre',1.4871255056128097,103.72438547599789),(121,'Opp Shell Kiosk @ Jalan Tun Abdul Razak',1.4887834830210198,103.72764307910049),(122,'aft Shell Kiosk @ Jalan Tun Abdul Razak',1.4884998356693775,103.72760379017922),(123,'CIMB Bank',1.4888638795941063,103.71242062086549),(124,'Klinik Kesihatan Tampoi',1.4925296181173713,103.70708612019975),(125,'bef Shell Kiosk @ Kampung Pasir',1.4925322994125712,103.70707002694427),(126,'SK Kampung Pasir',1.4989947483511965,103.6980312919993),(127,'Opp Pulai View Condo',1.500912032218495,103.69531386622876),(128,'bef KIP Mart',1.5082150994789085,103.68916128086431),(129,'Opp Paradigm Mall',1.516395250789313,103.6837138895428),(130,'bef McDonald\'s',1.5230889877416085,103.67895937664424),(131,'aft Jalan Sri Skudai',1.548816799334225,103.65409455093105),(132,'bef UTM Main Gate',1.5568669736349259,103.63801336191919),(133,'UTM Main Gate (Exit)',1.5567743097422382,103.63729839383352),(134,'Opp AEON Taman Universiti',1.5419187249489392,103.62971573495227),(135,'Kulai Terminal',1.6626828053288385,103.59889110796522),(136,'Kulai Centre Point',1.6613642865126417,103.60372737912934),(137,'Opp SBS Enterprises (M) Sdn Bhd',1.6541744853842373,103.60971038276091),(138,'Opp Public Bank @ Jalan Susur Kulai 2',1.6509304328430152,103.61148553732649),(139,'Opp Pertubuhan Peladang Kawasan Kulai',1.6452580216482706,103.61649637358444),(140,'Opp Hospital Temenggong Seri Maharaja Tun Ibrahim Kulaijaya',1.6398209133282802,103.62466463309562),(141,'Opp Jalan Cermai',1.6359493158863123,103.62993165279192),(142,'Opp Stor JKR (D) Kulaijaya',1.633014316152999,103.63349819512037),(143,'Opp Wang Loo Motor Sdn Bhd',1.628655062754551,103.63807709630609),(144,'Opp Pejabat Lembaga Lebuhraya Malaysia',1.6203723172849367,103.64614936801505),(145,'Masjid Jamek Pekan Senai',1.6059365939653953,103.64761480488822),(146,'Opp Deway Motor Trading',1.6131991987249765,103.64710738509358),(147,'aft Jalan Kelah',1.6295962449739738,103.63695517790576),(148,'TJ Mart',1.6335971426643172,103.63241743186276),(149,'aft Jalan Cermai 7',1.635335030874363,103.63004451042003),(150,'bef Hospital Temenggong Seri Maharaja Tun Ibrahim Kulaijaya',1.6396010400006824,103.62474653372412),(151,'SMK Kulai Besar',1.6455913464676681,103.61572207605488),(152,'aft Persiaran Indahpura 4',1.6476804172092263,103.61361307604972),(153,'Persatuan Hokkien Kulai',1.651406692568061,103.61086172023629),(154,'Opp Arked Kulai',1.6608994486573931,103.60422582209408);
/*!40000 ALTER TABLE `BusStop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Edge`
--

DROP TABLE IF EXISTS `Edge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Edge` (
  `EdgeID` int unsigned NOT NULL AUTO_INCREMENT,
  `FromBusStopID` int unsigned NOT NULL,
  `ToBusStopID` int unsigned NOT NULL,
  `RouteID` int unsigned NOT NULL,
  PRIMARY KEY (`EdgeID`),
  UNIQUE KEY `Edge_UN` (`EdgeID`),
  KEY `Edge_FK` (`FromBusStopID`),
  KEY `Edge_FK_1` (`ToBusStopID`),
  KEY `Edge_FK_2` (`RouteID`),
  CONSTRAINT `Edge_FK` FOREIGN KEY (`FromBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Edge_FK_1` FOREIGN KEY (`ToBusStopID`) REFERENCES `BusStop` (`BusStopID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Edge_FK_2` FOREIGN KEY (`RouteID`) REFERENCES `BusRoute` (`RouteID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Edge`
--

LOCK TABLES `Edge` WRITE;
/*!40000 ALTER TABLE `Edge` DISABLE KEYS */;
/*!40000 ALTER TABLE `Edge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Schedule`
--

DROP TABLE IF EXISTS `Schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Schedule` (
  `ScheduleID` int unsigned NOT NULL AUTO_INCREMENT,
  `RouteID` int unsigned NOT NULL,
  `Time` time NOT NULL,
  PRIMARY KEY (`ScheduleID`),
  UNIQUE KEY `Schedule_UN` (`ScheduleID`),
  KEY `Schedule_FK` (`RouteID`),
  CONSTRAINT `Schedule_FK` FOREIGN KEY (`RouteID`) REFERENCES `BusRoute` (`RouteID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=171 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Schedule`
--

LOCK TABLES `Schedule` WRITE;
/*!40000 ALTER TABLE `Schedule` DISABLE KEYS */;
INSERT INTO `Schedule` VALUES (1,1,'06:00:00'),(2,1,'06:25:00'),(3,1,'06:50:00'),(4,1,'07:15:00'),(5,1,'07:40:00'),(6,1,'08:05:00'),(7,1,'08:30:00'),(8,1,'09:00:00'),(9,1,'09:30:00'),(10,1,'10:00:00'),(11,1,'10:30:00'),(12,1,'11:00:00'),(13,1,'11:30:00'),(14,1,'12:00:00'),(15,1,'12:30:00'),(16,1,'13:00:00'),(17,1,'13:30:00'),(18,1,'14:00:00'),(19,1,'14:30:00'),(20,1,'15:00:00'),(21,1,'15:30:00'),(22,1,'16:00:00'),(23,1,'16:30:00'),(24,1,'17:00:00'),(25,1,'17:30:00'),(26,1,'18:00:00'),(27,1,'18:30:00'),(28,1,'19:00:00'),(29,1,'19:30:00'),(30,1,'20:00:00'),(31,1,'20:40:00'),(32,1,'21:20:00'),(33,1,'22:00:00'),(34,19,'06:00:00'),(35,19,'07:00:00'),(36,19,'08:00:00'),(37,19,'09:00:00'),(38,19,'10:00:00'),(39,19,'11:00:00'),(40,19,'12:00:00'),(41,19,'13:00:00'),(42,19,'14:00:00'),(43,19,'15:00:00'),(44,19,'16:00:00'),(45,19,'17:00:00'),(46,52,'06:00:00'),(47,52,'07:10:00'),(48,52,'08:30:00'),(49,52,'09:45:00'),(50,52,'11:00:00'),(51,52,'12:30:00'),(52,52,'13:45:00'),(53,52,'15:00:00'),(54,52,'16:30:00'),(55,52,'17:45:00'),(56,52,'19:00:00'),(57,79,'06:00:00'),(58,79,'07:00:00'),(59,79,'07:30:00'),(60,79,'08:30:00'),(61,79,'09:30:00'),(62,79,'10:30:00'),(63,79,'11:00:00'),(64,79,'12:00:00'),(65,79,'13:00:00'),(66,79,'14:00:00'),(67,79,'15:00:00'),(68,79,'16:00:00'),(69,79,'16:30:00'),(70,79,'17:30:00'),(71,79,'18:00:00'),(72,79,'19:00:00'),(73,102,'06:00:00'),(74,102,'06:20:00'),(75,102,'06:40:00'),(76,102,'07:00:00'),(77,102,'07:30:00'),(78,102,'08:00:00'),(79,102,'08:30:00'),(80,102,'09:00:00'),(81,102,'09:30:00'),(82,102,'10:00:00'),(83,102,'10:30:00'),(84,102,'11:00:00'),(85,102,'11:30:00'),(86,102,'12:00:00'),(87,102,'12:30:00'),(88,102,'13:00:00'),(89,102,'13:30:00'),(90,102,'14:00:00'),(91,102,'14:30:00'),(92,102,'15:00:00'),(93,102,'15:30:00'),(94,102,'16:00:00'),(95,102,'16:30:00'),(96,102,'17:00:00'),(97,102,'17:30:00'),(98,102,'18:00:00'),(99,102,'18:30:00'),(100,102,'19:00:00'),(101,102,'19:30:00'),(102,102,'20:00:00'),(103,111,'06:15:00'),(104,111,'06:35:00'),(105,111,'06:55:00'),(106,111,'07:15:00'),(107,111,'07:45:00'),(108,111,'08:15:00'),(109,111,'08:45:00'),(110,111,'09:15:00'),(111,111,'09:45:00'),(112,111,'10:15:00'),(113,111,'10:45:00'),(114,111,'11:15:00'),(115,111,'11:45:00'),(116,111,'12:15:00'),(117,111,'12:45:00'),(118,111,'13:15:00'),(119,111,'13:45:00'),(120,111,'14:15:00'),(121,111,'14:45:00'),(122,111,'15:15:00'),(123,111,'15:45:00'),(124,111,'16:15:00'),(125,111,'16:45:00'),(126,111,'17:15:00'),(127,111,'17:45:00'),(128,111,'18:15:00'),(129,111,'18:45:00'),(130,111,'19:15:00'),(131,111,'19:45:00'),(132,111,'20:15:00'),(133,123,'06:00:00'),(134,123,'07:10:00'),(135,123,'08:10:00'),(136,123,'09:10:00'),(137,123,'10:10:00'),(138,123,'11:10:00'),(139,123,'12:10:00'),(140,123,'13:10:00'),(141,123,'14:10:00'),(142,123,'15:10:00'),(143,123,'16:10:00'),(144,123,'17:10:00'),(145,123,'18:20:00'),(146,123,'19:15:00'),(147,148,'06:00:00'),(148,148,'06:45:00'),(149,148,'08:00:00'),(150,148,'09:00:00'),(151,148,'10:00:00'),(152,148,'11:00:00'),(153,148,'12:00:00'),(154,148,'13:00:00'),(155,148,'14:00:00'),(156,148,'15:00:00'),(157,148,'16:00:00'),(158,148,'17:00:00'),(159,148,'18:00:00'),(160,148,'19:10:00'),(161,176,'06:00:00'),(162,176,'09:00:00'),(163,176,'12:00:00'),(164,176,'14:30:00'),(165,176,'17:00:00'),(166,206,'07:15:00'),(167,206,'10:15:00'),(168,206,'13:15:00'),(169,206,'15:45:00'),(170,206,'18:15:00');
/*!40000 ALTER TABLE `Schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Weight`
--

DROP TABLE IF EXISTS `Weight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Weight` (
  `WeightID` int unsigned NOT NULL AUTO_INCREMENT,
  `EdgeID` int unsigned NOT NULL,
  `Weight` double NOT NULL DEFAULT '0',
  `Type` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`WeightID`),
  UNIQUE KEY `Weight_UN` (`WeightID`),
  KEY `Weight_FK` (`EdgeID`),
  CONSTRAINT `Weight_FK` FOREIGN KEY (`EdgeID`) REFERENCES `Edge` (`EdgeID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Weight`
--

LOCK TABLES `Weight` WRITE;
/*!40000 ALTER TABLE `Weight` DISABLE KEYS */;
/*!40000 ALTER TABLE `Weight` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-15  0:14:13
