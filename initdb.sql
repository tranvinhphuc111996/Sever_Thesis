/* Table thiết bị */
CREATE TABLE Device (
	SocetSID varchar(50) PRIMARY KEY,
	DeviceID varchar(16) ,
	Description TEXT,

);
/* Table nhân viên */
CREATE TABLE Employee (
	EmployeeName nvarchar(1024),
	EmployeeID varchar(16) PRIMARY KEY,
	CardID varchar(16),
	-- FingerID varchar(16),
	PicName varchar(50),
	EmployeeBirthDate DATE
);

CREATE TABLE Work (
	DeviceID varchar(16) references Devices(DeviceID),
	CardID varchar(16) references Employee(CardID),
	-- FingerID varchar(16) references Employee(FingerID), 
	ImageID varchar(16) references Employee(ImageID),
	EntryTime DATETIME, /* Thời gian quét thẻ */
	EntryTimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (CardID,EntryTimeStamp)
);

/* Thẻ chưa đăng ký */
CREATE TABLE UnRegistered (
	CardID varchar(16) PRIMARY KEY
);

/* Table quản trị */
CREATE TABLE Administrator (
	username nvarchar(1024) PRIMARY KEY,
	password nvarchar(1024)
);

/* username/password dùng để test */
INSERT INTO Administrator VALUES ('admin', 'admin');