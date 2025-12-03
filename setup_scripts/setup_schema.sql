-- =============================================
-- Library Database Schema Creation Script
-- =============================================
-- This script creates the database and all tables
-- Run this FIRST before loading CSV data
-- =============================================

USE master;
GO

-- Drop existing database if it exists
IF DB_ID(N'SharedData') IS NOT NULL
BEGIN
    ALTER DATABASE [SharedData] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [SharedData];
END
GO

-- Create database (using default file locations)
CREATE DATABASE [SharedData];
GO

USE [SharedData];
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

-- Ensure schema exists
IF SCHEMA_ID('dbo') IS NULL EXEC('CREATE SCHEMA dbo');
GO

-- Drop tables in FK-safe order
IF OBJECT_ID('dbo.Checkout','U') IS NOT NULL DROP TABLE dbo.Checkout;
IF OBJECT_ID('dbo.LibraryCard','U') IS NOT NULL DROP TABLE dbo.LibraryCard;
IF OBJECT_ID('dbo.Customer','U') IS NOT NULL DROP TABLE dbo.Customer;
IF OBJECT_ID('dbo.BookCopy','U') IS NOT NULL DROP TABLE dbo.BookCopy;
IF OBJECT_ID('dbo.BookCopyCondition','U') IS NOT NULL DROP TABLE dbo.BookCopyCondition;
IF OBJECT_ID('dbo.Book','U') IS NOT NULL DROP TABLE dbo.Book;
IF OBJECT_ID('dbo.Genre','U') IS NOT NULL DROP TABLE dbo.Genre;
IF OBJECT_ID('dbo.Author','U') IS NOT NULL DROP TABLE dbo.Author;
GO

-- =============================================
-- Create Tables
-- =============================================

CREATE TABLE dbo.Author (
    AuthorID       INT            IDENTITY(1,1) NOT NULL,
    FirstName      NVARCHAR(100)  NOT NULL,
    LastName       NVARCHAR(100)  NOT NULL,
    CONSTRAINT PK_Author PRIMARY KEY (AuthorID),
    CONSTRAINT UQ_Author_Full UNIQUE (FirstName, LastName)
);
GO

CREATE TABLE dbo.Genre (
    GenreID        INT           IDENTITY(1,1) NOT NULL,
    Name           NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_Genre PRIMARY KEY (GenreID),
    CONSTRAINT UQ_Genre_Name UNIQUE (Name)
);
GO

CREATE TABLE dbo.Book (
    BookID         INT            IDENTITY(1,1) NOT NULL,
    ISBN           CHAR(13)       NOT NULL,
    CoverImg       NVARCHAR(500)  NULL,
    AuthorID       INT            NOT NULL,
    Title          NVARCHAR(400)  NOT NULL,
    GenreID        INT            NOT NULL,
    CONSTRAINT PK_Book PRIMARY KEY (BookID),
    CONSTRAINT UQ_Book_ISBN UNIQUE (ISBN),
    CONSTRAINT UQ_Book_Author_Title UNIQUE (AuthorID, Title),
    CONSTRAINT FK_Book_Author FOREIGN KEY (AuthorID) REFERENCES dbo.Author(AuthorID),
    CONSTRAINT FK_Book_Genre FOREIGN KEY (GenreID) REFERENCES dbo.Genre(GenreID)
);
GO

CREATE TABLE dbo.BookCopyCondition (
    ConditionID    INT            IDENTITY(1,1) NOT NULL,
    Condition      NVARCHAR(50)   NOT NULL,
    CONSTRAINT PK_BookCopyCondition PRIMARY KEY (ConditionID),
    CONSTRAINT UQ_BookCopyCondition_Condition UNIQUE (Condition)
);
GO

CREATE TABLE dbo.BookCopy (
    BookCopyID     INT           IDENTITY(1,1) NOT NULL,
    BookID         INT           NOT NULL,
    ConditionID    INT           NOT NULL,
    PurchasedDate  DATE          NOT NULL,
    CONSTRAINT PK_BookCopy PRIMARY KEY (BookCopyID),
    CONSTRAINT FK_BookCopy_Book FOREIGN KEY (BookID) REFERENCES dbo.Book(BookID),
    CONSTRAINT FK_BookCopy_Condition FOREIGN KEY (ConditionID) REFERENCES dbo.BookCopyCondition(ConditionID)
);
GO

CREATE TABLE dbo.Customer (
    CustomerID     INT            IDENTITY(1,1) NOT NULL,
    EmailAddress   NVARCHAR(320)  NOT NULL,
    FirstName      NVARCHAR(100)  NOT NULL,
    LastName       NVARCHAR(100)  NOT NULL,
    CONSTRAINT PK_Customer PRIMARY KEY (CustomerID),
    CONSTRAINT UQ_Customer_Email UNIQUE (EmailAddress)
);
GO

CREATE TABLE dbo.LibraryCard (
    LibraryCardID  INT  IDENTITY(1,1) NOT NULL,
    CustomerID     INT  NOT NULL,
    Inactive       BIT  NOT NULL,
    CONSTRAINT PK_LibraryCard PRIMARY KEY (LibraryCardID),
    CONSTRAINT FK_LibraryCard_Customer FOREIGN KEY (CustomerID) REFERENCES dbo.Customer(CustomerID)
);
GO

CREATE TABLE dbo.Checkout (
    CheckoutID          INT  IDENTITY(1,1) NOT NULL,
    BookCopyID          INT  NOT NULL,
    LenderLibraryCardID INT  NOT NULL,
    CheckoutDate        DATE NOT NULL,
    DueDate             DATE NOT NULL,
    DateReturned        DATE NULL,
    CONSTRAINT PK_Checkout PRIMARY KEY (CheckoutID),
    CONSTRAINT FK_Checkout_Copy FOREIGN KEY (BookCopyID) REFERENCES dbo.BookCopy(BookCopyID),
    CONSTRAINT FK_Checkout_Card FOREIGN KEY (LenderLibraryCardID) REFERENCES dbo.LibraryCard(LibraryCardID)
);
GO

PRINT 'Database schema created successfully!';
PRINT 'Tables created: Author, Genre, Book, BookCopyCondition, BookCopy, Customer, LibraryCard, Checkout';
PRINT 'Ready for CSV data loading.';
GO
