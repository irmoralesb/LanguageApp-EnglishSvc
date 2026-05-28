/* Creates application databases on the SQL Server instance (run as SA via db-init container). */
SET NOCOUNT ON;

IF DB_ID(N'IdentityDB') IS NULL
BEGIN
    CREATE DATABASE IdentityDB;
END;

IF DB_ID(N'PrepositionsDB') IS NULL
BEGIN
    CREATE DATABASE PrepositionsDB;
END;

IF DB_ID(N'EnglishDB') IS NULL
BEGIN
    CREATE DATABASE EnglishDB;
END;
