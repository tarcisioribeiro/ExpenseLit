-- MySQL dump 10.13  Distrib 8.0.41, for Linux (x86_64)
--
-- Host: localhost    Database: financas
-- ------------------------------------------------------
-- Server version	8.0.41-0ubuntu0.22.04.1

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
-- Current Database: `financas`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `financas` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `financas`;

--
-- Table structure for table `anos`
--

DROP TABLE IF EXISTS `anos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `anos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ano` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `anos`
--

LOCK TABLES `anos` WRITE;
/*!40000 ALTER TABLE `anos` DISABLE KEYS */;
INSERT INTO `anos` VALUES (1,2020),(2,2021),(3,2022),(4,2023),(5,2024),(6,2025),(7,2026),(8,2027),(9,2028);
/*!40000 ALTER TABLE `anos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beneficiados`
--

DROP TABLE IF EXISTS `beneficiados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `beneficiados` (
  `id_beneficiado` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_beneficiado`),
  UNIQUE KEY `chave_beneficiado` (`nome`,`documento`,`telefone`),
  UNIQUE KEY `idx_beneficiado` (`nome`,`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beneficiados`
--

--
-- Table structure for table `cartao_credito`
--

DROP TABLE IF EXISTS `cartao_credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cartao_credito` (
  `id_cartao` int NOT NULL AUTO_INCREMENT,
  `nome_cartao` varchar(100) NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `nome_titular` varchar(100) NOT NULL,
  `proprietario_cartao` varchar(100) NOT NULL,
  `documento_titular` varchar(11) NOT NULL,
  `data_validade` date NOT NULL,
  `codigo_seguranca` varchar(3) NOT NULL,
  `limite_credito` decimal(10,2) NOT NULL DEFAULT '0.00',
  `limite_maximo` decimal(10,2) NOT NULL DEFAULT '0.00',
  `conta_associada` varchar(100) NOT NULL,
  `inativo` varchar(1) DEFAULT 'N',
  PRIMARY KEY (`id_cartao`),
  UNIQUE KEY `chave_cartao` (`numero_cartao`,`documento_titular`,`conta_associada`),
  UNIQUE KEY `unq_cartao_credito_nome_cartao` (`nome_cartao`,`numero_cartao`),
  KEY `fk_cartao_credito_usuarios` (`proprietario_cartao`,`documento_titular`),
  KEY `fk_cartao_credito_contas` (`conta_associada`),
  CONSTRAINT `fk_cartao_credito_contas` FOREIGN KEY (`conta_associada`) REFERENCES `contas` (`nome_conta`) ON DELETE RESTRICT,
  CONSTRAINT `fk_cartao_credito_usuarios` FOREIGN KEY (`proprietario_cartao`, `documento_titular`) REFERENCES `usuarios` (`nome`, `documento`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cartao_credito`
--

--
-- Table structure for table `contas`
--

DROP TABLE IF EXISTS `contas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contas` (
  `id_conta` int NOT NULL AUTO_INCREMENT,
  `nome_conta` varchar(100) NOT NULL,
  `tipo_conta` varchar(50) NOT NULL,
  `proprietario_conta` varchar(100) NOT NULL,
  `documento_proprietario_conta` varchar(11) NOT NULL,
  `caminho_arquivo_imagem` text,
  `inativa` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id_conta`),
  UNIQUE KEY `chave_conta` (`nome_conta`,`tipo_conta`,`proprietario_conta`,`documento_proprietario_conta`),
  KEY `fk_contas_usuarios` (`proprietario_conta`,`documento_proprietario_conta`),
  CONSTRAINT `fk_contas_usuarios` FOREIGN KEY (`proprietario_conta`, `documento_proprietario_conta`) REFERENCES `usuarios` (`nome`, `documento`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contas`
--

--
-- Table structure for table `credores`
--

DROP TABLE IF EXISTS `credores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credores` (
  `id_credor` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_credor`),
  UNIQUE KEY `chave_credor` (`nome`,`documento`,`telefone`),
  UNIQUE KEY `idx_credor` (`nome`,`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credores`
--

--
-- Table structure for table `despesas`
--

DROP TABLE IF EXISTS `despesas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `despesas` (
  `id_despesa` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Despesa',
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `conta` varchar(100) NOT NULL,
  `proprietario_despesa` varchar(100) NOT NULL,
  `documento_proprietario_despesa` varchar(11) NOT NULL,
  `pago` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id_despesa`),
  UNIQUE KEY `chave_despesa` (`valor`,`data`,`horario`,`categoria`,`conta`,`proprietario_despesa`,`documento_proprietario_despesa`),
  KEY `fk_despesas_contas` (`conta`),
  CONSTRAINT `fk_despesas_contas` FOREIGN KEY (`conta`) REFERENCES `contas` (`nome_conta`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `despesas`
--

--
-- Table structure for table `despesas_cartao_credito`
--

DROP TABLE IF EXISTS `despesas_cartao_credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `despesas_cartao_credito` (
  `id_despesa_cartao` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Despesa Cartão',
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `cartao` varchar(100) NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `proprietario_despesa_cartao` varchar(100) NOT NULL,
  `doc_proprietario_cartao` varchar(11) NOT NULL,
  `parcela` int NOT NULL DEFAULT (_utf8mb4'1'),
  `pago` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id_despesa_cartao`),
  UNIQUE KEY `chave_despesa_cartao` (`valor`,`data`,`horario`,`categoria`,`cartao`,`parcela`),
  KEY `fk_despesas_cartao_credito` (`cartao`,`numero_cartao`),
  CONSTRAINT `fk_despesas_cartao_credito` FOREIGN KEY (`cartao`, `numero_cartao`) REFERENCES `cartao_credito` (`nome_cartao`, `numero_cartao`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `despesas_cartao_credito`
--

--
-- Table structure for table `emprestimos`
--

DROP TABLE IF EXISTS `emprestimos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emprestimos` (
  `id_emprestimo` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL,
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `valor_pago` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) DEFAULT NULL,
  `conta` varchar(100) NOT NULL,
  `devedor` varchar(100) NOT NULL,
  `documento_devedor` varchar(11) NOT NULL,
  `credor` varchar(100) NOT NULL,
  `documento_credor` varchar(11) NOT NULL,
  `pago` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id_emprestimo`),
  UNIQUE KEY `chave_emprestimo` (`valor`,`data`,`horario`,`categoria`,`conta`,`devedor`,`credor`),
  KEY `fk_emprestimos_contas` (`conta`),
  KEY `fk_beneficiado_emprestimo` (`devedor`,`documento_devedor`),
  KEY `fk_credor_emprestimo` (`credor`,`documento_credor`),
  CONSTRAINT `fk_beneficiado_emprestimo` FOREIGN KEY (`devedor`, `documento_devedor`) REFERENCES `beneficiados` (`nome`, `documento`) ON UPDATE CASCADE,
  CONSTRAINT `fk_credor_emprestimo` FOREIGN KEY (`credor`, `documento_credor`) REFERENCES `credores` (`nome`, `documento`) ON DELETE RESTRICT,
  CONSTRAINT `fk_emprestimos_contas` FOREIGN KEY (`conta`) REFERENCES `contas` (`nome_conta`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emprestimos`
--

--
-- Table structure for table `fechamentos_cartao`
--

DROP TABLE IF EXISTS `fechamentos_cartao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fechamentos_cartao` (
  `id_fechamento_cartao` int NOT NULL AUTO_INCREMENT,
  `nome_cartao` varchar(100) NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `documento_titular` varchar(11) NOT NULL,
  `ano` year NOT NULL,
  `mes` varchar(20) NOT NULL,
  `data_comeco_fatura` date NOT NULL,
  `data_fim_fatura` date NOT NULL,
  `fechado` varchar(1) DEFAULT 'N',
  PRIMARY KEY (`id_fechamento_cartao`),
  UNIQUE KEY `chave_fechamento_cartao` (`numero_cartao`,`documento_titular`,`ano`,`mes`),
  KEY `fk_fechamentos_cartao` (`nome_cartao`,`numero_cartao`),
  CONSTRAINT `fk_fechamentos_cartao` FOREIGN KEY (`nome_cartao`, `numero_cartao`) REFERENCES `cartao_credito` (`nome_cartao`, `numero_cartao`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fechamentos_cartao`
--

--
-- Table structure for table `logs_atividades`
--

DROP TABLE IF EXISTS `logs_atividades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs_atividades` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `data_log` date NOT NULL DEFAULT (curdate()),
  `horario_log` time NOT NULL DEFAULT (curtime()),
  `usuario_log` varchar(25) NOT NULL,
  `tipo_log` varchar(100) NOT NULL,
  `conteudo_log` text NOT NULL,
  PRIMARY KEY (`id_log`),
  KEY `fk_logs_atividades_usuarios` (`usuario_log`),
  CONSTRAINT `fk_logs_atividades_usuarios` FOREIGN KEY (`usuario_log`) REFERENCES `usuarios` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_atividades`
--

--
-- Table structure for table `meses`
--

DROP TABLE IF EXISTS `meses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_mes` tinyint NOT NULL,
  `nome_mes` varchar(20) NOT NULL,
  `abreviacao` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meses`
--

LOCK TABLES `meses` WRITE;
/*!40000 ALTER TABLE `meses` DISABLE KEYS */;
INSERT INTO `meses` VALUES (1,1,'Janeiro','Jan'),(2,2,'Fevereiro','Fev'),(3,3,'Março','Mar'),(4,4,'Abril','Abr'),(5,5,'Maio','Mai'),(6,6,'Junho','Jun'),(7,7,'Julho','Jul'),(8,8,'Agosto','Ago'),(9,9,'Setembro','Set'),(10,10,'Outubro','Out'),(11,11,'Novembro','Nov'),(12,12,'Dezembro','Dez');
/*!40000 ALTER TABLE `meses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modelos_conta`
--

DROP TABLE IF EXISTS `modelos_conta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modelos_conta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome_instituicao` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos_conta`
--

LOCK TABLES `modelos_conta` WRITE;
/*!40000 ALTER TABLE `modelos_conta` DISABLE KEYS */;
INSERT INTO `modelos_conta` VALUES (1,'Banco do Brasil'),(2,'Bradesco'),(3,'Ben Visa Vale'),(4,'Caixa Econômica Federal'),(5,'Carteira'),(6,'Ifood Benefícios'),(7,'Itaú'),(8,'Nubank'),(9,'Mercado Pago'),(10,'Picpay'),(11,'Santander'),(12,'Sicoob');
/*!40000 ALTER TABLE `modelos_conta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receitas`
--

DROP TABLE IF EXISTS `receitas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receitas` (
  `id_receita` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Receita',
  `valor` decimal(10,2) DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `conta` varchar(100) NOT NULL,
  `proprietario_receita` varchar(100) NOT NULL,
  `documento_proprietario_receita` varchar(11) NOT NULL,
  `recebido` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id_receita`),
  UNIQUE KEY `chave_despesa` (`valor`,`data`,`horario`,`categoria`,`conta`,`proprietario_receita`,`documento_proprietario_receita`),
  KEY `fk_receitas_contas` (`conta`),
  CONSTRAINT `fk_receitas_contas` FOREIGN KEY (`conta`) REFERENCES `contas` (`nome_conta`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receitas`
--

--
-- Table structure for table `transferencias`
--

DROP TABLE IF EXISTS `transferencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transferencias` (
  `id_transferencia` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Transferência',
  `valor` decimal(10,2) NOT NULL,
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `conta_origem` varchar(100) NOT NULL,
  `conta_destino` varchar(100) NOT NULL,
  `proprietario_transferencia` varchar(100) NOT NULL,
  `documento_proprietario_transferencia` varchar(11) NOT NULL,
  `transferido` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id_transferencia`),
  UNIQUE KEY `chave_transferencia` (`valor`,`data`,`horario`,`categoria`,`conta_origem`,`conta_destino`),
  KEY `fk_transferencias_despesas` (`conta_origem`),
  KEY `fk_transferencias_receitas` (`conta_destino`),
  CONSTRAINT `fk_transferencias_despesas` FOREIGN KEY (`conta_origem`) REFERENCES `despesas` (`conta`) ON DELETE RESTRICT,
  CONSTRAINT `fk_transferencias_receitas` FOREIGN KEY (`conta_destino`) REFERENCES `receitas` (`conta`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transferencias`
--

LOCK TABLES `transferencias` WRITE;
/*!40000 ALTER TABLE `transferencias` DISABLE KEYS */;
/*!40000 ALTER TABLE `transferencias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `login` varchar(25) NOT NULL,
  `senha` varchar(100) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `sexo` char(1) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `chave_usuario` (`login`,`senha`),
  UNIQUE KEY `unq_usuarios_nome` (`nome`,`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

--
-- Table structure for table `usuarios_logados`
--

DROP TABLE IF EXISTS `usuarios_logados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_logados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `nome_completo` varchar(255) NOT NULL,
  `documento` varchar(50) NOT NULL,
  `data_login` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sessao_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sessao_id` (`sessao_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_logados`
--

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-22 22:46:09
