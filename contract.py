# 🗳️ VOTING SMART CONTRACT 🗳️  
# This smart contract allows users to create a voting event with up to 4 options,  
# enables participants to vote, and keeps track of the votes securely.  
# It ensures that each user can vote only once and that voting happens within the specified time.  

# Import necessary modules from Algopy (Smart contract framework for Algorand)  
# These modules help in defining contract logic, handling transactions, and storing state.  
from algopy import ARC4Contract, UInt64, String, LocalState, Txn, Global, op  
from algopy.arc4 import abimethod  

# ---------------------------------------------------  
# 🗳️ VOTING SMART CONTRACT 🗳️  
# This contract allows users to create a vote, set options, and manage voting sessions.  
# ---------------------------------------------------  

class Voting(ARC4Contract):  # 🏛️ Main smart contract class  
    # ---------------------------------------------------  
    # 🛢️ STATE VARIABLES (Persistent Storage on Blockchain)  
    # These variables will store important data about the voting process.  
    # ---------------------------------------------------  
    title: String  # 📌 Title of the voting event  
    description: String  # 📌 Description of the voting event  
    noOfOptions: UInt64  # 📌 Number of available voting options (max 4)  
    option1: String  # 📌 Name of option 1  
    option2: String  # 📌 Name of option 2  
    option3: String  # 📌 Name of option 3  
    option4: String  # 📌 Name of option 4  
    option1Votes: UInt64  # 📌 Vote count for option 1  
    option2Votes: UInt64  # 📌 Vote count for option 2  
    option3Votes: UInt64  # 📌 Vote count for option 3  
    option4Votes: UInt64  # 📌 Vote count for option 4  
    startsAt: UInt64  # 📌 Timestamp when voting starts  
    endsAt: UInt64  # 📌 Timestamp when voting ends  
    vote_status: UInt64  # 📌 Voting status: 0 = Not started, 1 = Active  
    localState: LocalState[UInt64]  # 📌 Stores voter choices (ensuring one vote per user)  

    def __init__(self) -> None:  # 🏗️ Constructor: Initializes the contract with default values  
        """  
        Initializes the contract with default values.  
        This function is automatically executed when the contract is deployed.  
        """  
        self.title = String("")  # ❌ No title yet  
        self.description = String("")  # ❌ No description yet  
        self.noOfOptions = UInt64(0)  # 🔢 No options set yet  
        self.option1 = String("")  # ❌ No option 1 yet  
        self.option2 = String("")  # ❌ No option 2 yet  
        self.option3 = String("")  # ❌ No option 3 yet  
        self.option4 = String("")  # ❌ No option 4 yet  
        self.option1Votes = UInt64(0)  # 🔢 Votes for option 1  
        self.option2Votes = UInt64(0)  # 🔢 Votes for option 2  
        self.option3Votes = UInt64(0)  # 🔢 Votes for option 3  
        self.option4Votes = UInt64(0)  # 🔢 Votes for option 4  
        self.startsAt = UInt64(0)  # 🕒 Voting start time  
        self.endsAt = UInt64(0)  # 🕒 Voting end time  
        self.vote_status = UInt64(0)  # 🚦 Voting status (0 = Not started)  
        self.localState = LocalState(UInt64)  # 🛑 Tracks whether a user has voted  

    # ---------------------------------------------------  
    # 🗳️ FUNCTION: Create a Vote  
    # Allows an admin to create a vote with up to 4 options and a deadline.  
    # ---------------------------------------------------  
    @abimethod()  
    def create_vote(self, title: String, description: String, noOfOptions: UInt64,  
                    option1: String, option2: String, option3: String, option4: String, endsAt: UInt64) -> None:  
        """  
        Creates a voting event with a title, description, options, and an end time.  

        Parameters:  
        - title (String): The title of the voting event.  
        - description (String): A brief description of the voting event.  
        - noOfOptions (UInt64): The number of options (must be between 2 and 4).  
        - option1 (String): The first option.  
        - option2 (String): The second option.  
        - option3 (String): The third option (optional).  
        - option4 (String): The fourth option (optional).  
        - endsAt (UInt64): The timestamp when voting ends.  

        Raises:  
        - AssertionError: If a vote already exists.  
        - AssertionError: If the number of options is not between 2 and 4.  
        - AssertionError: If the end time is in the past.  
        """  
        assert self.vote_status == 0, "❌ Vote already created!"  
        assert noOfOptions >= 2 and noOfOptions <= 4, "❌ Number of options must be between 2 and 4!"  
        assert Global.latest_timestamp < endsAt, "❌ Invalid end time!"  

        # 📝 Store vote details  
        self.title = title  
        self.description = description  
        self.noOfOptions = noOfOptions  
        self.option1 = option1  
        self.option2 = option2  
        self.option3 = option3  
        self.option4 = option4  
        self.option1Votes = UInt64(0)  
        self.option2Votes = UInt64(0)  
        self.option3Votes = UInt64(0)  
        self.option4Votes = UInt64(0)  
        self.startsAt = Global.latest_timestamp  
        self.endsAt = endsAt  
        self.vote_status = UInt64(1)  # ✅ Voting is now active  

    # ---------------------------------------------------  
    # 🗳️ FUNCTION: Vote  
    # Allows users to cast their vote for one of the available options.  
    # ---------------------------------------------------  
    @abimethod()  
    def vote(self, option: UInt64) -> None:  
        """  
        A user casts a vote for an option.  

        Parameters:  
        - option (UInt64): The option number (1-4).  

        Raises:  
        - AssertionError: If voting is not active.  
        - AssertionError: If the user has already voted.  
        - AssertionError: If the selected option is invalid.  
        """  
        assert Global.latest_timestamp < self.endsAt, "❌ Voting has ended!"  
        assert Global.latest_timestamp > self.startsAt, "❌ Voting has not started!"  
        assert option >= 1 and option <= self.noOfOptions, "❌ Invalid option!"  

        val, exist = self.localState.maybe(Txn.sender)  # 🔍 Check if user has voted  
        assert not exist, "❌ You have already voted!"  

        self.localState[Txn.sender] = option  # 📝 Store the user's vote  

        # ✅ Increment vote count based on the selected option  
        if option == 1:
            self.option1Votes += 1
        elif option == 2:
            self.option2Votes += 1
        elif option == 3:
            self.option3Votes += 1
        elif option == 4:
            self.option4Votes += 1
        else:
            op.exit(0)
    # ---------------------------------------------------  
    # ⚙️ FUNCTION: Opt-In  
    # Allows users to opt-in to the contract before voting.  
    # ---------------------------------------------------  
    @abimethod(allow_actions=['OptIn'])  
    def opt_in(self) -> None:  
        """  
        Allows users to opt-in to the smart contract.  
        This is required before they can vote.  
        """  
        pass  
