USE SharedData;
GO

-- Book Popularity
CREATE OR ALTER PROCEDURE BookPopularityProc
	@FirstDate DATE,
	@LastDate DATE
AS

WITH PeriodCheckout AS (
    SELECT
        YEAR(CO.CheckoutDate) AS Year,
        MONTH(CO.CheckoutDate) AS Month,
        B.BookID,
        COUNT(*) AS PeriodCheckouts
    FROM Checkout CO
    JOIN BookCopy BC ON CO.BookCopyID = BC.BookCopyID
    JOIN Book B ON B.BookID = BC.BookID
    WHERE CO.CheckoutDate BETWEEN @FirstDate AND @LastDate
    GROUP BY
        YEAR(CO.CheckoutDate),
        MONTH(CO.CheckoutDate),
        B.BookID
),
LifetimeCheckout AS (
    SELECT
        B.BookID,
        COUNT(*) AS LifetimeCheckouts
    FROM Checkout CO
    JOIN BookCopy BC ON CO.BookCopyID = BC.BookCopyID
    JOIN Book B ON B.BookID = BC.BookID
    GROUP BY B.BookID
)
SELECT
    PC.Year,
    PC.Month,
    B.BookID,
    B.Title,
    PC.PeriodCheckouts,
    LiC.LifetimeCheckouts,
    RANK() OVER (
        PARTITION BY PC.Year, PC.Month
        ORDER BY PC.PeriodCheckouts DESC
    ) AS PeriodRank
FROM PeriodCheckout PC
JOIN LifetimeCheckout LiC ON LiC.BookID = PC.BookID
JOIN BookCopy BC ON BC.BookID = PC.BookID
JOIN Book B ON B.BookID = BC.BookID
Group BY B.BookID, PC.Year, PC.Month, B.Title, PC.PeriodCheckouts, LiC.LifetimeCheckouts
ORDER BY
    pc.Year,
    pc.Month,
    PeriodRank,
    B.BookID;
GO

-- Customer Activity
CREATE OR ALTER PROCEDURE CustomerActivityProc
	@FirstDate DATE,
	@LastDate DATE
AS

WITH PeriodCustomer AS (
    SELECT
        YEAR(co.CheckoutDate) AS Year,
        MONTH(co.CheckoutDate) AS Month,
        lc.CustomerID,
        COUNT(*) AS PeriodCheckouts
    FROM Checkout co
    JOIN LibraryCard lc ON co.LenderLibraryCardID = lc.LibraryCardID
    WHERE co.CheckoutDate BETWEEN @FirstDate AND @LastDate
    GROUP BY
        YEAR(co.CheckoutDate),
        MONTH(co.CheckoutDate),
        lc.CustomerID
),
LifetimeCustomer AS (
    SELECT
        lc.CustomerID,
        COUNT(*) AS LifetimeCheckouts
    FROM Checkout co
    JOIN LibraryCard lc ON co.LenderLibraryCardID = lc.LibraryCardID
    GROUP BY lc.CustomerID
)
SELECT
    pc.Year,
    pc.Month,
    c.CustomerID,
    c.FirstName + ' ' + c.LastName AS CustomerName,
    pc.PeriodCheckouts,
    lc2.LifetimeCheckouts,
    RANK() OVER (
        PARTITION BY pc.Year, pc.Month
        ORDER BY pc.PeriodCheckouts DESC
    ) AS PeriodRank
FROM PeriodCustomer pc
JOIN LifetimeCustomer lc2 ON lc2.CustomerID = pc.CustomerID
JOIN Customer c ON c.CustomerID = pc.CustomerID
ORDER BY
    pc.Year,
    pc.Month,
    PeriodRank,
    c.CustomerID;
GO

-- Overdue Behavior
CREATE OR ALTER PROCEDURE OverdueBehaviorProc
	@FirstDate DATE,
	@LastDate DATE
AS

WITH PeriodCustomer AS (
    SELECT
        YEAR(CO.CheckoutDate) AS Year,
        MONTH(CO.CheckoutDate) AS Month,
        LC.CustomerID,
        COUNT(*) AS PeriodOverdueCount
    FROM Checkout CO
    JOIN LibraryCard LC ON CO.LenderLibraryCardID = LC.LibraryCardID
    WHERE co.CheckoutDate BETWEEN @FirstDate AND @LastDate
    AND CO.DateReturned > Co.DueDate
    GROUP BY
        YEAR(CO.CheckoutDate),
        MONTH(CO.CheckoutDate),
        LC.CustomerID
),
LifetimeCustomer AS (
    SELECT
        LC.CustomerID,
        COUNT(*) AS LifetimeOverdueCount
    FROM Checkout CO
    JOIN LibraryCard LC ON CO.LenderLibraryCardID = LC.LibraryCardID
    Where CO.DateReturned > CO.DueDate
    GROUP BY LC.CustomerID
)
SELECT
    PC.Year,
    PC.Month,
    C.CustomerID,
    C.FirstName + ' ' + C.LastName AS CustomerName,
    PC.PeriodOverdueCount,
    LiC.LifetimeOverdueCount,
    RANK() OVER (
        PARTITION BY PC.Year, PC.Month
        ORDER BY PC.PeriodOverdueCount DESC
    ) AS PeriodRank
FROM PeriodCustomer PC
JOIN LifetimeCustomer LiC ON LiC.CustomerID = PC.CustomerID
JOIN Customer C ON C.CustomerID = PC.CustomerID
ORDER BY
    PC.Year,
    PC.Month,
    PeriodRank,
    C.CustomerID;
GO

-- Genre Circulation
CREATE OR ALTER PROCEDURE GenreCirculationProc
	@FirstDate DATE,
	@LastDate DATE
AS

WITH PeriodGenre AS (
    SELECT
        YEAR(co.CheckoutDate) AS Year,
        MONTH(co.CheckoutDate) AS Month,
        g.GenreID,
        COUNT(*) AS PeriodCheckoutCount
    FROM Checkout co
    JOIN BookCopy bc ON co.BookCopyID = bc.BookCopyID
    JOIN Book b ON bc.BookID = b.BookID
    JOIN Genre g ON b.GenreID = g.GenreID
    WHERE co.CheckoutDate BETWEEN @FirstDate AND @LastDate
    GROUP BY
        YEAR(co.CheckoutDate),
        MONTH(co.CheckoutDate),
        g.GenreID
),
LifetimeGenre AS (
    SELECT
        g.GenreID,
        COUNT(*) AS LifetimeCheckoutCount
    FROM Checkout co
    JOIN BookCopy bc ON co.BookCopyID = bc.BookCopyID
    JOIN Book b ON bc.BookID = b.BookID
    JOIN Genre g ON b.GenreID = g.GenreID
    GROUP BY g.GenreID
)
SELECT
    pg.Year,
    pg.Month,
    g.GenreID,
    g.Name AS GenreName,
    pg.PeriodCheckoutCount,
    lg.LifetimeCheckoutCount,
    RANK() OVER (
        PARTITION BY pg.Year, pg.Month
        ORDER BY pg.PeriodCheckoutCount DESC
    ) AS PeriodRank
FROM PeriodGenre pg
JOIN LifetimeGenre lg ON lg.GenreID = pg.GenreID
JOIN Genre g ON g.GenreID = pg.GenreID
ORDER BY
    pg.Year,
    pg.Month,
    PeriodRank,
    g.GenreID;
GO
