-- MySQL dump 10.13  Distrib 9.3.0, for Linux (x86_64)
--
-- Host: localhost    Database: financas
-- ------------------------------------------------------
-- Server version	9.3.0

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

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `financas` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

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
  `bissexto` varchar(1) DEFAULT (_utf8mb4'N'),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `anos`
--

LOCK TABLES `anos` WRITE;
/*!40000 ALTER TABLE `anos` DISABLE KEYS */;
INSERT INTO `anos` VALUES (1,2024,'S'),(2,2025,'N'),(3,2026,'N'),(4,2027,'N'),(5,2028,'S');
/*!40000 ALTER TABLE `anos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beneficiados`
--

DROP TABLE IF EXISTS `beneficiados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `beneficiados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) DEFAULT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_beneficiado` (`nome`,`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beneficiados`
--

LOCK TABLES `beneficiados` WRITE;
/*!40000 ALTER TABLE `beneficiados` DISABLE KEYS */;
/*!40000 ALTER TABLE `beneficiados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cartao_credito`
--

DROP TABLE IF EXISTS `cartao_credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cartao_credito` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome_cartao` varchar(100) NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `nome_titular` varchar(100) NOT NULL,
  `id_prop_cartao` int NOT NULL,
  `doc_titular_cartao` varchar(11) NOT NULL,
  `data_validade` date NOT NULL,
  `codigo_seguranca` varchar(3) NOT NULL,
  `limite_credito` decimal(10,2) NOT NULL DEFAULT '0.00',
  `limite_maximo` decimal(10,2) NOT NULL DEFAULT '0.00',
  `id_conta_associada` int NOT NULL,
  `inativo` varchar(1) DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_cartao` (`numero_cartao`,`doc_titular_cartao`,`id_conta_associada`),
  UNIQUE KEY `unq_cartao_credito_nome_cartao` (`nome_cartao`,`numero_cartao`),
  UNIQUE KEY `unq_cartao_credito_id_prop_cartao` (`id_prop_cartao`,`doc_titular_cartao`),
  UNIQUE KEY `unq_cartao_credito_id` (`id`,`numero_cartao`),
  KEY `fk_cartao_credito_conta` (`id_conta_associada`),
  CONSTRAINT `fk_cartao_credito_conta` FOREIGN KEY (`id_conta_associada`) REFERENCES `contas` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cartao_credito`
--

LOCK TABLES `cartao_credito` WRITE;
/*!40000 ALTER TABLE `cartao_credito` DISABLE KEYS */;
/*!40000 ALTER TABLE `cartao_credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_despesa`
--

DROP TABLE IF EXISTS `categorias_despesa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_despesa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_despesa`
--

LOCK TABLES `categorias_despesa` WRITE;
/*!40000 ALTER TABLE `categorias_despesa` DISABLE KEYS */;
INSERT INTO `categorias_despesa` VALUES (1,'Casa'),(2,'Eletroeletrônicos'),(3,'Entretenimento'),(4,'Lazer'),(5,'Presente'),(6,'Restaurante'),(7,'Saúde'),(8,'Serviços'),(9,'Supermercado'),(10,'Transporte'),(11,'Vestuário');
/*!40000 ALTER TABLE `categorias_despesa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_receita`
--

DROP TABLE IF EXISTS `categorias_receita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_receita` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_receita`
--

LOCK TABLES `categorias_receita` WRITE;
/*!40000 ALTER TABLE `categorias_receita` DISABLE KEYS */;
INSERT INTO `categorias_receita` VALUES (1,'Ajuste'),(2,'Depósito'),(3,'Entretenimento'),(4,'Prêmio'),(5,'Salário'),(6,'Vale'),(7,'Saúde'),(8,'Rendimentos');
/*!40000 ALTER TABLE `categorias_receita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_transferencia`
--

DROP TABLE IF EXISTS `categorias_transferencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_transferencia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_transferencia`
--

LOCK TABLES `categorias_transferencia` WRITE;
/*!40000 ALTER TABLE `categorias_transferencia` DISABLE KEYS */;
INSERT INTO `categorias_transferencia` VALUES (1,'DOC'),(2,'TED'),(3,'Pix');
/*!40000 ALTER TABLE `categorias_transferencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contas`
--

DROP TABLE IF EXISTS `contas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_tipo_conta` int NOT NULL,
  `nome_conta` varchar(100) NOT NULL,
  `id_prop_conta` int NOT NULL,
  `doc_prop_conta` varchar(11) NOT NULL,
  `caminho_imagem` varchar(255) NOT NULL DEFAULT 'default.png',
  `inativa` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unq_conta` (`id_tipo_conta`,`nome_conta`,`id_prop_conta`,`doc_prop_conta`),
  CONSTRAINT `fk_id_tipo_conta` FOREIGN KEY (`id_tipo_conta`) REFERENCES `tipos_conta` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contas`
--

LOCK TABLES `contas` WRITE;
/*!40000 ALTER TABLE `contas` DISABLE KEYS */;
/*!40000 ALTER TABLE `contas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credores`
--

DROP TABLE IF EXISTS `credores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_credor` (`nome`,`documento`,`telefone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credores`
--

LOCK TABLES `credores` WRITE;
/*!40000 ALTER TABLE `credores` DISABLE KEYS */;
/*!40000 ALTER TABLE `credores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `despesas`
--

DROP TABLE IF EXISTS `despesas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `despesas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Despesa',
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `id_conta` int NOT NULL,
  `id_prop_despesa` int NOT NULL,
  `doc_prop_despesa` varchar(11) NOT NULL,
  `pago` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_despesa` (`valor`,`data`,`horario`,`categoria`,`id_conta`,`id_prop_despesa`,`doc_prop_despesa`),
  KEY `fk_proprietario_despesa` (`id_prop_despesa`,`doc_prop_despesa`),
  KEY `fk_despesas_contas` (`id_conta`),
  CONSTRAINT `fk_despesas_contas` FOREIGN KEY (`id_conta`) REFERENCES `contas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `despesas`
--

LOCK TABLES `despesas` WRITE;
/*!40000 ALTER TABLE `despesas` DISABLE KEYS */;
/*!40000 ALTER TABLE `despesas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `despesas_cartao_credito`
--

DROP TABLE IF EXISTS `despesas_cartao_credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `despesas_cartao_credito` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Despesa Cartão',
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `id_cartao` int NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `id_prop_despesa_cartao` int NOT NULL,
  `doc_prop_cartao` varchar(11) NOT NULL,
  `parcela` int NOT NULL DEFAULT '1',
  `pago` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_despesa_cartao` (`valor`,`data`,`horario`,`categoria`,`parcela`),
  KEY `fk_prop_despesa_cartao` (`id_prop_despesa_cartao`,`doc_prop_cartao`),
  KEY `fk_cartao_despesa` (`id_cartao`),
  CONSTRAINT `fk_cartao_despesa` FOREIGN KEY (`id_cartao`) REFERENCES `cartao_credito` (`id`),
  CONSTRAINT `fk_prop_despesa_cartao` FOREIGN KEY (`id_prop_despesa_cartao`, `doc_prop_cartao`) REFERENCES `cartao_credito` (`id_prop_cartao`, `doc_titular_cartao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `despesas_cartao_credito`
--

LOCK TABLES `despesas_cartao_credito` WRITE;
/*!40000 ALTER TABLE `despesas_cartao_credito` DISABLE KEYS */;
/*!40000 ALTER TABLE `despesas_cartao_credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emprestimos`
--

DROP TABLE IF EXISTS `emprestimos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emprestimos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL,
  `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
  `valor_pago` decimal(10,2) NOT NULL DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) DEFAULT NULL,
  `id_conta` int NOT NULL,
  `id_beneficiado` int NOT NULL,
  `doc_beneficiado` varchar(11) NOT NULL,
  `id_credor` int NOT NULL,
  `doc_credor` varchar(11) NOT NULL,
  `pago` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_emprestimo` (`valor`,`data`,`horario`,`categoria`,`id_conta`,`id_beneficiado`,`id_credor`),
  KEY `fk_beneficiado_emprestimo` (`id_beneficiado`),
  KEY `fk_conta_emprestimo` (`id_conta`),
  KEY `fk_credor_emprestimo` (`id_credor`),
  CONSTRAINT `fk_beneficiado_emprestimo` FOREIGN KEY (`id_beneficiado`) REFERENCES `beneficiados` (`id`),
  CONSTRAINT `fk_conta_emprestimo` FOREIGN KEY (`id_conta`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_credor_emprestimo` FOREIGN KEY (`id_credor`) REFERENCES `credores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emprestimos`
--

LOCK TABLES `emprestimos` WRITE;
/*!40000 ALTER TABLE `emprestimos` DISABLE KEYS */;
/*!40000 ALTER TABLE `emprestimos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fechamentos_cartao`
--

DROP TABLE IF EXISTS `fechamentos_cartao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fechamentos_cartao` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_cartao` int NOT NULL,
  `numero_cartao` varchar(16) NOT NULL,
  `id_prop_cartao` int NOT NULL,
  `doc_prop_cartao` varchar(11) NOT NULL,
  `ano` int NOT NULL,
  `mes` varchar(100) NOT NULL,
  `data_comeco_fatura` date NOT NULL,
  `data_fim_fatura` date NOT NULL,
  `fechado` varchar(1) DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_fechamento_cartao` (`numero_cartao`,`doc_prop_cartao`,`ano`,`mes`),
  KEY `fk_fechamentos_cartao` (`id_cartao`,`numero_cartao`),
  KEY `fk_ano_fechamento` (`ano`),
  KEY `fk_mes_fechamento` (`mes`),
  CONSTRAINT `fk_chave_cartao` FOREIGN KEY (`id_cartao`, `numero_cartao`) REFERENCES `cartao_credito` (`id`, `numero_cartao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fechamentos_cartao`
--

LOCK TABLES `fechamentos_cartao` WRITE;
/*!40000 ALTER TABLE `fechamentos_cartao` DISABLE KEYS */;
/*!40000 ALTER TABLE `fechamentos_cartao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs_atividades`
--

DROP TABLE IF EXISTS `logs_atividades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs_atividades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `data_log` date NOT NULL DEFAULT (curdate()),
  `horario_log` time NOT NULL DEFAULT (curtime()),
  `id_usuario_log` int NOT NULL,
  `tipo_log` varchar(100) NOT NULL,
  `conteudo_log` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_logs_atividades_usuarios` (`id_usuario_log`),
  CONSTRAINT `fk_logs_atividades_usuarios` FOREIGN KEY (`id_usuario_log`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_atividades`
--

LOCK TABLES `logs_atividades` WRITE;
/*!40000 ALTER TABLE `logs_atividades` DISABLE KEYS */;
/*!40000 ALTER TABLE `logs_atividades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meses`
--

DROP TABLE IF EXISTS `meses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meses` (
  `id` int NOT NULL AUTO_INCREMENT,
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
INSERT INTO `meses` VALUES (1,'Janeiro','Jan'),(2,'Fevereiro','Fev'),(3,'Março','Mar'),(4,'Abril','Abr'),(5,'Maio','Mai'),(6,'Junho','Jun'),(7,'Julho','Jul'),(8,'Agosto','Ago'),(9,'Setembro','Set'),(10,'Outubro','Out'),(11,'Novembro','Nov'),(12,'Dezembro','Dez');
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
  `id_tipo` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_id_tipo` (`id_tipo`),
  CONSTRAINT `fk_tipo_conta` FOREIGN KEY (`id_tipo`) REFERENCES `tipos_conta` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos_conta`
--

LOCK TABLES `modelos_conta` WRITE;
/*!40000 ALTER TABLE `modelos_conta` DISABLE KEYS */;
INSERT INTO `modelos_conta` VALUES (1,'Nubank',1),(2,'Sicoob',1),(3,'Mercado Pago',1),(4,'Ifood Benefícios',4),(5,'Caixa Econômica Federal',3);
/*!40000 ALTER TABLE `modelos_conta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receitas`
--

DROP TABLE IF EXISTS `receitas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receitas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Receita',
  `valor` decimal(10,2) DEFAULT '0.00',
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `id_conta` int NOT NULL,
  `id_prop_receita` int NOT NULL,
  `doc_prop_receita` varchar(11) NOT NULL,
  `recebido` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_despesa` (`valor`,`data`,`horario`,`categoria`,`id_conta`,`id_prop_receita`,`doc_prop_receita`),
  KEY `fk_proprietario_receita` (`id_prop_receita`,`doc_prop_receita`),
  KEY `fk_receitas_contas` (`id_conta`),
  CONSTRAINT `fk_receitas_contas` FOREIGN KEY (`id_conta`) REFERENCES `contas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receitas`
--

LOCK TABLES `receitas` WRITE;
/*!40000 ALTER TABLE `receitas` DISABLE KEYS */;
/*!40000 ALTER TABLE `receitas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_conta`
--

DROP TABLE IF EXISTS `tipos_conta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_conta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_conta`
--

LOCK TABLES `tipos_conta` WRITE;
/*!40000 ALTER TABLE `tipos_conta` DISABLE KEYS */;
INSERT INTO `tipos_conta` VALUES (1,'Conta Corrente'),(2,'Conta Salário'),(3,'Fundo de Garantia'),(4,'Vale Alimentação');
/*!40000 ALTER TABLE `tipos_conta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transferencias`
--

DROP TABLE IF EXISTS `transferencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transferencias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL DEFAULT 'Transferência',
  `valor` decimal(10,2) NOT NULL,
  `data` date NOT NULL DEFAULT (curdate()),
  `horario` time NOT NULL DEFAULT (curtime()),
  `categoria` varchar(100) NOT NULL,
  `id_conta_origem` int NOT NULL,
  `id_conta_destino` int NOT NULL,
  `id_prop_transferencia` int NOT NULL,
  `doc_prop_transferencia` varchar(11) NOT NULL,
  `transferido` char(1) NOT NULL DEFAULT 'S',
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_transferencia` (`valor`,`data`,`horario`,`categoria`,`id_conta_origem`,`id_conta_destino`),
  KEY `fk_transferencias_despesas` (`id_conta_origem`),
  KEY `fk_transferencias_receitas` (`id_conta_destino`),
  CONSTRAINT `fk_transferencias_despesas` FOREIGN KEY (`id_conta_origem`) REFERENCES `contas` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_transferencias_receitas` FOREIGN KEY (`id_conta_destino`) REFERENCES `contas` (`id`) ON DELETE RESTRICT
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
  `id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(25) NOT NULL,
  `senha` varchar(100) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `documento` varchar(11) NOT NULL,
  `telefone` varchar(11) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `sexo` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chave_usuario` (`login`,`senha`),
  UNIQUE KEY `unq_usuarios_nome` (`nome`,`documento`),
  UNIQUE KEY `unq_usuarios_id` (`id`,`documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_logados`
--

DROP TABLE IF EXISTS `usuarios_logados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_logados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `doc_usuario` varchar(50) NOT NULL,
  `nome_completo` varchar(100) NOT NULL,
  `data_login` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sessao_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sessao_id` (`sessao_id`),
  KEY `fk_usuario_logado` (`id_usuario`,`doc_usuario`),
  CONSTRAINT `fk_usuario_logado` FOREIGN KEY (`id_usuario`, `doc_usuario`) REFERENCES `usuarios` (`id`, `documento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_logados`
--

LOCK TABLES `usuarios_logados` WRITE;
/*!40000 ALTER TABLE `usuarios_logados` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_logados` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-13 21:20:08
