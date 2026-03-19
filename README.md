# UniLink - Backend

UniLink is a Django-based backend project serving as the backend for a platform facilitating connections between students, universities, and professionals. It focuses on features like posts, relationships, chat, caching, and user-specific preferences such as skills and interests.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [App Modules](#app-modules)
- [Database Models](#database-models)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)

---

## Features

- **User Management**: Authentication, skills, and interests tracking via `apps.users`.
- **University Management**: Universities and their departments via `apps.universities`.
- **Social Networking**: Create posts, follow/unfollow users, and manage relationships.
- **Real-time Messaging**: Chat functionality with message model support.
- **Caching**: Faster and optimized data retrieval/reduce heavy queries.
- **Tagging System**: Add/remove tags for posts using `apps.posts`.

---

## Tech Stack

- **Python**: v3.13.3
- **Django**: Latest release
- **Redis**: Caching support
- **SQLite/MySQL/PostgreSQL**: Configurable database
- **Virtual Environment Management**: `virtualenv`

---

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup the database**:
   Make changes in the `settings.py` file to configure your database (e.g., `SQLite`, `PostgreSQL`, `MySQL`).

5. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000`

---

## App Modules

### 1. `apps.core`
Core utility functions and configurations of the project.

### 2. `apps.users`
User authentication and profile management (skills, interests, etc.).

### 3. `apps.posts`
Post creation, tagging, and management of posts and tags.

### 4. `apps.universities`
University and department models to organize educational content.

### 5. `apps.relationships`
Manage relationships between users (e.g., follow/unfollow).

### 6. `apps.caching`
Caching mechanisms using Redis for optimized queries.

### 7. `apps.chat`
Message models for real-time chat.

---

## Database Models

The project uses several models distributed across different apps:

- **Users** (`apps.users.models.Users`): Handles authentication and user-specific data.
- **UserSkills & UserInterests**: Models for managing user skills and interests.
- **Posts & Tags**: Handles posts and their associated tags.
- **Universities & Departments**: Manage university information.
- **Message**: Define the structure for real-time messaging functionality.

---

## Directory Structure

Below is an overview of the main files and directories in the project:
