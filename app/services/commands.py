# Simple command pattern for user actions

class Command:
    """Base command class"""
    def execute(self):
        pass
    
    def undo(self):
        pass

class CreateUserCommand(Command):
    """Command to create a new user"""
    def __init__(self, user_data):
        self.user_data = user_data
        self.created_user = None
    
    def execute(self):
        # Would create user in database
        print(f"Creating user: {self.user_data.get('username')}")
        self.created_user = self.user_data
        return self.created_user
    
    def undo(self):
        if self.created_user:
            print(f"Removing user: {self.created_user.get('username')}")
            self.created_user = None

class DonateCommand(Command):
    """Command to process a donation"""
    def __init__(self, donation_data):
        self.donation_data = donation_data
        self.processed = False
    
    def execute(self):
        print(f"Processing donation of ${self.donation_data.get('amount')}")
        self.processed = True
        return True
    
    def undo(self):
        if self.processed:
            print(f"Reversing donation of ${self.donation_data.get('amount')}")
            self.processed = False

class CommandInvoker:
    """Executes commands"""
    def __init__(self):
        self.history = []
    
    def execute_command(self, command):
        result = command.execute()
        self.history.append(command)
        return result
    
    def undo_last(self):
        if self.history:
            last_command = self.history.pop()
            last_command.undo()