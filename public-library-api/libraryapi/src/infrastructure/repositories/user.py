"""A repository for user entity."""


from typing import Any

from pydantic import UUID4

from src.infrastructure.utils.password import hash_password
from src.core.domain.user import UserIn, User
from src.core.repositories.iuser import IUserRepository
from src.db import database, user_table


class UserRepository(IUserRepository):
    """An implementation of repository class for user."""

    async def register_user(self, user: UserIn) -> Any | None:
        """A method registering new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            Any | None: The new user object.
        """

        if await self.get_by_email(user.email):
            return None

        user.password = hash_password(user.password)

        query = user_table.insert().values(**user.model_dump())
        new_user_uuid = await database.execute(query)

        return await self.get_by_uuid(new_user_uuid)

    async def get_by_uuid(self, uuid: UUID4) -> Any | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID5): UUID of the user.

        Returns:
            Any | None: The user object if exists.
        """

        query = user_table \
            .select() \
            .where(user_table.c.id == uuid)
        user = await database.fetch_one(query)

        return user

    async def get_by_email(self, email: str) -> Any | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            Any | None: The user object if exists.
        """

        query = user_table \
            .select() \
            .where(user_table.c.email == email)
        user = await database.fetch_one(query)

        return user
    
    async def update_user(self, uuid: UUID4, user_data: UserIn) -> User | None:
        """A method to update user details."""

        # Query to update user data in the database
        query = user_table.update().where(user_table.c.id == uuid).values(**user_data.dict())
        await database.execute(query)

        # Fetch the updated user by UUID
        return await self.get_by_uuid(uuid)

    async def delete_user(self, uuid: UUID4) -> bool:
        """A method to delete a user by UUID."""

        # Query to delete user from the database
        query = user_table.delete().where(user_table.c.id == uuid)
        result = await database.execute(query)

        # Return True if a row was deleted, else False
        return result > 0