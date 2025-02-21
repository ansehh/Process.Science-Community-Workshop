# process-mining-example

# MySQL Docker Setup

This repository contains a **MySQL 8.0** database setup using **Docker Compose**. The configuration ensures a persistent database with automatic initialization.

## 🚀 Getting Started

### 1️⃣ Prerequisites
Make sure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo/process-mining-example.git
cd process-mining-example
```

### 3️⃣ Start MySQL Container
Run the following command to start MySQL:
```sh
docker-compose up -d
```
This will:
- Pull and run a MySQL 8.0 container.
- Create a new database named **`demo-erp-system`**.
- Use credentials defined in `docker-compose.yml`.

#### ✅ Verify MySQL is Running:
```sh
docker ps
```
You should see a container named **mysql_db** running.

### 4️⃣ Connect to MySQL

#### 🔹 Option 1: Using Docker Exec
```sh
docker exec -it mysql_db mysql -u user -p
```
Enter the **password** (`userpassword`) when prompted.

To connect as root:
```sh
docker exec -it mysql_db mysql -u root -p
```
Enter **rootpassword** when prompted.

#### 🔹 Option 2: Using a Local MySQL Client
If you have MySQL installed on your local machine:
```sh
mysql -h 127.0.0.1 -P 3306 -u user -p
```
Or, as root:
```sh
mysql -h 127.0.0.1 -P 3306 -u root -p
```

### 5️⃣ Verify Database
After connecting, check if the database exists:
```sql
SHOW DATABASES;
USE demo-erp-system;
```

## 🛠 Stopping & Removing Containers
To stop the MySQL container:
```sh
docker-compose down
```
This will **stop and remove** the container but keep the data stored in the volume.

To remove the **data as well**:
```sh
docker volume rm process-mining-example_mysql_data
```

## 📂 Directory Structure
```
process-mining-example/
│── docker-compose.yml   # Docker Compose file to set up MySQL
│── init/                # Directory for initialization SQL scripts (if needed)
│── README.md            # This documentation
```

## 📌 Environment Variables
These values are set in `docker-compose.yml`:
| Variable              | Value          |
|----------------------|---------------|
| MYSQL_ROOT_PASSWORD  | rootpassword  |
| MYSQL_DATABASE       | demo-erp-system |
| MYSQL_USER          | user          |
| MYSQL_PASSWORD      | userpassword  |

## 🖥 Connecting via GUI (MySQL Workbench / DBeaver)
If you prefer using a GUI tool, use these credentials:
- **Host:** `127.0.0.1`
- **Port:** `3306`
- **Username:** `user`
- **Password:** `userpassword`
- **Database:** `demo-erp-system`


