@echo off
echo Starting all services...

REM Start PostgreSQL if not running
echo Starting PostgreSQL...
net start postgresql-x64-16

REM Start Spring Boot backend
echo Starting Spring Boot backend...
cd backend
call mvnw.cmd spring-boot:run
cd ..

echo All services started!
