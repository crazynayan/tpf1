# TPF Analyzer Tool
A tool to document TPF Assembler code. 
## Contents
1. [Software Requirements](#software-requirements)
2. [Installation Instructions](#installation-instructions)
3. [Using The TPF Analyzer Tool](#using-the-tpf-analyzer-tool)
4. [Shutting Down The Application](#shutting-down-the-application)
5. [Batch Files For Restarting Application](#batch-files-for-restarting-application)
6. [Restarting the Application](#restarting-the-application)
7. [Conclusion](#conclusion)

## Software Requirements
1. Windows 11 Operating System
2. Windows Terminal 
3. Git (Latest Stable version)
4. Python (Latest Stable version)
5. Node.js (Latest Stable version)
6. d20_source folder from info@crazyideas.co.in
### Another Operating System
* The tool will also work on other operating systems like Linux or Mac. 
* The installation instructions here are specific to Windows, and these instructions have been tested on Windows.
* For other operating systems, the user needs to be familiar equivalent instruction mentioned here.

## Installation Instructions
(All commands are given on Windows Terminal)
### 1.Start A New Terminal Window 
- Let's call this Command Window 2 - Backend Shell
- Go to the folder on which you want to Install the project (for e.g. H:\My Drive\PythonProjects)
### 2. Clone The Repository From Git
- `git clone https://github.com/crazynayan/tpf1.git`
- This will create a folder tpf1 with all the source code.
### 3. Rename The Folder
- This is an optional step
- `ren tpf1 TpfAnalyzer`
### 4. Make It The Current Directory
- `cd TpfAnalyzer`
### 5. Create a Python Virtual Environment
- `python -m venv venv`
- This will create a folder venv with the python virtual environment.
### 6. Activate The Virtual Environment
- `venv\Scripts\activate`
- Windows Terminal prompt will show that you are in venv virtual environment.
### 7. Install Dependencies
- `pip install -r requirements.txt`
- This will install the dependencies in the venv folder.
### 8. Setup d20_source
- Unzip the provided d20_source folder.
- Copy the folder in your current project folder.
### 9. Setup Git
- This step is only required if you wish to contribute to this open source project.
- `git init .`
- Use your GitHub email to set up your git credentials (if not already done).
- `git config --global user.email "you@example.com"`
- `git config --global user.name "Your Name"`
- Check your remote connection `git remote -v`
- If not connected with  https://github.com/crazynayan/tpf1.git then you would need to manually connect it.
### 10. Installing And Initializing Firebase
- Go to Firebase (http://console.firebase.google.com) 
  - Login with your google account
  - Create a new project. 
  - Note down the project id. (For e.g. tpf-analyzer)
- Return to Command Window 2 - Backend shell
  - Install Firebase tools `npm install -g firebase-tools`
  - Login Firebase by following prompts and login via your google account `firebase login`
  - Initialize Firebase 
  - `firebase init `
  - Select Emulators
  - Select Firestore Emulator 
  - Use the existing project id and select the project id created at http://console.firebase.google.com. (tpf-analyzer)
  - Say Yes to Emulator UI
  - Use any available port for emulator UI
  - Download the emulators now
### 11. Setup Environment Variables
- `set SERVER_URL=call_local`
- `set FIRESTORE_EMULATOR_HOST=127.0.0.1:8080`
- `set FIRESTORE_EMULATOR_PROJECT_ID=tpf-analyzer`
  - Use the project id created in Step 10. Here we have used the project id 'tpf-analyzer'
### 12. Start The Firestore Emulator 
- Open a new terminal window (Let's call it Command Window 1 - FirestoreEmulator)
- Go to the project directory (H:\My Drive\PythonProjects\TPFAnalyzer)
- `firebase emulators:start --only firestore --export-on-exit --import=./saved-data`
- Please confirm the firestore has started on the same address on which the FIRESTORE_EMULATOR_HOST environment variable is set on [step 11](#11-setup-environment-variables) above.
- This command ensures that the data is saved across session in firestore emulator. 
- In order for data to persist, it is important that the firestore emulator is closed properly via Ctl-C.
### 13. Run Unit Test
- Return to the project window (Command Window 2 — Backend Shell).
- `python -m unittest d21_backend.p8_test.test_local.test_execution.test_ts29 -v`
- You should see 19 tests ran successfully.
### 14. Start The Flask Shell
- Flask shell works with the backend app so set the environment variable appropriately
- `set FLASK_APP=d21_backend.p7_flask_app:tpf1_app`
- `flask shell`
- You will now be in the python prompt where you can give python commands to create users, etc.
### 15. Create Your User Account
- `create_user(email="you@example.com",initial="YO",domain="general")`
- Note down the password for later login. Or reset the password using the following steps.
### 16. Reset Password
- `u = User.objects.filter_by(email="you@example.com").first()`
- `u.set_password("simple")`
- `u.save()`
### 17. Initialize Segments
- `tpf.init_all_asm_segments_in_base()`
- `tpf.init_all_asm_segments_in_domain("general")`
### 18. Start The Web Server
- Open a new terminal window (Let's call it Command Window 3 — Web Server).
- Go to the project directory. `H:` `cd \My Drive\PythonProjects\TPFAnalyzer`
- Activate the virtual environment. `venv\Scripts\activate`
- Set the environment variables as per [Step 11](#11-setup-environment-variables) above and set FLASK_APP.
  - `set SERVER_URL=call_local`
  - `set FIRESTORE_EMULATOR_HOST=127.0.0.1:8080`
  - `set FIRESTORE_EMULATOR_PROJECT_ID=tpf-analyzer`
  - `set FLASK_APP=d29_frontend.flask_app:tpf2_app`
-  Start the web server `flask run`
- This will give you an http endpoint. You can Ctrl-Click it to view the page in the browser.

## Using The TPF Analyzer Tool
(All instructions are for browser web pages)
### 1. Login
- Click login and login using your created credential.
- Login: you@example.com
- Password: simple
- You should be able to see the home page with all the options at the top.
### 2. Check Segments
- Click on Segments in the NavBar
- You should see a segment list.
- Search TSJ1 and click on TSJ1 button to open its assembly. It should say 100% supported.
- Now we will try to understand what this program is doing and document it.
### 3. Create Test Data
- Click on Test Data in Nav Bar
- Click Create Test Data
  - Name of Test Data: GN01 - TSJ1 - PNR Other Agency Access
  - Segment Name: TSJ1
  - Leave the remaining fields blank
  - Click on Save & Add Further Data
- Click on Add Debug Segments
  - Enter Segment names: TSJ1
  - Click on Save & Continue
- Click on Add Output Fields
  - Field Name: EBRS01
  - Click on Search
  - Leave all fields as it is
  - Click on Save & Continue
- Click on +AAA (Add AAA Field) in Input Fields
  - Select variation (from Drop down): New Variation
  - New Variation Name: BOM1
  - Enter Multiple Fields: WA0POR:006F2F,WA0FNS:10
  - Click on Save & Continue
- Click on +AAA (Add AAA Field)
  - Select variation (from Drop down): New Variation
  - New Variation Name: BOM2
  - Enter Multiple Fields: WA0POR:006F2E,WA0FNS:10
  - Click on Save & Continue
- Click on +AAA (Add AAA Field)
  - Select variation (from Drop down): New Variation
  - New Variation Name: Airline
  - Enter Multiple Fields: WA0POR:006F2F,WA0FNS:00
  - Click on Save & Continue
- Click on +AAA (Add AAA Field)
  - Select variation (from Drop down): New Variation
  - New Variation Name: BOM3
  - Enter Multiple Fields: WA0POR:00017F,WA0FNS:10
  - Click on Save & Continue
- Click on +Add PNR (in Input-PNR)
  - Select variation (from Drop down): New Variation
  - New Variation Name: Give to BOM3
  - Select type of PNR element: GROUP_PLAN
  - Leave the Enter PNR locator blank
  - Enter text: BJS-BOM3/GRANT ACCESS
  - Leave the last field blank
  - Click on Save & Continue
- Click on +Add PNR (in Input-PNR)
  - Select variation (from Drop down): New Variation
  - New Variation Name: Give to BOM1
  - Select type of PNR element: GROUP_PLAN
  - Leave the Enter PNR locator blank
  - Enter text: BJS-BOM1/GRANT ACCESS
  - Leave the last field blank
  - Click on Save & Continue
- Click on + Add Fixed File (in Input-Fixed Files)
  - Select variation (from Drop down): New Variation
  - New Variation Name: BOM3 to BOM1 reject
  - Fixed File - Macro Name: TJ0TJ 
  - Fixed File - Record ID: E3D1
  - Fixed File - File Type: 94
  - Fixed File - Ordinal Number: 383
  - Leave several fields as it is and go down to Pool File section
  - Pool File - Macro Name: IY1IY
  - Pool File - Record Id: C9E8
  - Pool File - Field in Fixed File where reference of this pool file will be stored: TJ0ATH
  - Leave the next three fields as it and go down to Pool File Item section
  - Pool File Item - Item Label: IY1ATH
  - Keep the Pool File Item checkbox unchecked.
  - Pool File Item - No of times you want this item to be repeated (1 to 100): 1
  - Pool File Item - Item Count Label: IY1CTR
  - Pool File - Item Field Data: IY9AON:00006F2F,IY9AGY:00
  - Click on Save & Continue
- Click on + Add Fixed File (in Input-Fixed Files)
  - Select variation (from Drop down): New Variation
  - New Variation Name: BOM3 to BOM1 allow
  - Fixed File - Macro Name: TJ0TJ 
  - Fixed File - Record ID: E3D1
  - Fixed File - File Type: 94
  - Fixed File - Ordinal Number: 383
  - Leave several fields as it is and go down to Pool File section
  - Pool File - Macro Name: IY1IY
  - Pool File - Record Id: C9E8
  - Pool File - Field in Fixed File where reference of this pool file will be stored: TJ0ATH
  - Leave the next three fields as it and go down to Pool File Item section
  - Pool File Item - Item Label: IY1ATH
  - Keep the Pool File Item checkbox unchecked.
  - Pool File Item - No of times you want this item to be repeated (1 to 100): 1
  - Pool File Item - Item Count Label: IY1CTR
  - Pool File - Item Field Data: IY9AON:00006F2F,IY9AGY:10
  - Click on Save & Continue
- Click on Return on Test Data View (button is at the top of the page)
### 4. Execute The Test Data
- Click on Run
- You will see the Execution Result with General Summary having 16 results.
- Scroll Down to review other results and at the bottom there is debug information.
- Click on Return To Test Data View (button is at the top of the page).
- Now we will save and document the results.
### 5. Document The Test Results
- Click on Save
  - Enter Test Result Name: GN01 - TSJ1 - PNR Other Agency Access - 16 Combinations of Access
  - Click on Save Test Result
- All the edits below are in the General summary section.
- Click on Edit for #1
  - Enter Comment: WHEN the PNR is Owned by BOM1 AND the PNR element gives access to BOM3 BUT the Security of BOM3 does not allow access to BOM1 THEN ET will fail due to security setting. 
  - Click on Save
- Click on Edit for #2
  - Enter Comment: WHEN the PNR is Owned by BOM1 AND the PNR element gives access to BOM3 AND the Security of BOM3 allows access to BOM1 THEN ET will pass agency access validation. 
  - Click on Save
- Click on Edit for #3
  - Enter Comment: WHEN the PNR is Owned by BOM1 AND the PNR element gives access to BOM1 THEN ET will passes agency access validation SINCE Security settings are not applicable in this case.
  - Click on Save
- Click on Edit for #4
  - Enter Comment: Same as #3
  - Click on Save
- Click on Edit for #5
  - Enter Comment: WHEN the PNR is Owned by BOM2 AND the PNR element gives access to BOM1 THEN ET will fail SINCE the security profile of BOM3 does NOT have an entry for BOM2 AND Security setting of BOM3 - to BOM1 is not applicable in this case.
  - Click on Save
- Click on Edit for #6
  - Enter Comment: Same as #5
  - Click on Save
- Click on Edit for #7
  - Enter Comment: Dump & exit since there is no security profile setup for BOM1 
  - Click on Save
- Click on Edit for #8
  - Enter Comment: Same as #7
  - Click on Save
- Click on Edit for #9
  - Enter Comment: ET passes agency access validation since the PNR is owned by airline. Airline owned PNR does NOT go through agency access validation. PNR element that give access to other cities is - ignored. Security profile of that agency is also NOT checked.
  - Click on Save
- Click on Edit for #10
  - Enter Comment: Same as #9 
  - Click on Save
- Click on Edit for #11
  - Enter Comment: Same as #9
  - Click on Save
- Click on Edit for #12
  - Enter Comment: Same as #9
  - Click on Save
- Click on Edit for #13
  - Enter Comment: WHEN the PNR is Owned by BOM3 AND the PNR element gives access to BOM3 THEN ET will passes agency access validation SINCE Security settings are not applicable in this case.
  - Click on Save
- Click on Edit for #14
  - Enter Comment: Same as #13
  - Click on Save
- Click on Edit for #15
  - Enter Comment: Same as #7 
  - Click on Save
- Click on Edit for #16
  - Enter Comment: Same as #7 
  - Click on Save
### 6. Run The Profiler
- Click on Profiler
  - Segment Name: TSJ1
  - Select Test Data: GN01 - TSJ1 - PNR Other Agency Access
  - Click on Run Profile
- You should see the documentation coverage of 79%
- Review the code to see the highlighted missing instruction
- Create new test data, execute it, then document it and check the profile again (Repeat Step 3 to 6) to improve on documentation coverage.

## Shutting Down The Application
### 1. Close The Web Server
- Go to Command Window 3 - Web Server
- Press Ctrl-C
### 2. Exit Shell
- Go to Command Window 2 - Backend Shell
- `exit()`
### 3. Close the Firestore Emulator
- Go to Command Window 1 - Firestore Emulator
- Press Ctrl-C

## Batch Files For Restarting Application
### 1. Web Server Batch File
- Create tpfanalyzer.bat on your home directory with the following code
```
@echo off
H:
cd \My Drive\PythonProjects\TPFAnalyzer
set FLASK_APP=d29_frontend.flask_app:tpf2_app
set SERVER_URL=call_local
set FIRESTORE_EMULATOR_PROJECT_ID=tpf-analyzer
set FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
venv\Scripts\activate
```
- Note: If you have created the project in a different path/drive and used a different project id then update the batch file accordingly.
### 2. Flask Shell Batch File
- Create tpfanalyzershell.bat on your home directory with the following code
```
@echo off
H:
cd \My Drive\PythonProjects\TPFAnalyzer
set FLASK_APP=d21_backend.p7_flask_app:tpf1_app
set FIRESTORE_EMULATOR_PROJECT_ID=tpf-analyzer
set FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
venv\Scripts\activate
```

## Restarting the Application
### 1. Command Window 1 - Firestore Emulator
```
tpfanalyzer
firebase emulators:start --only firestore --export-on-exit --import=./saved-data
```
### 2. Command Window 2 - Backend Shell
```
tpfanalyzershell
flask shell
```
### 3. Command Window 3 - Web Server
```
tpfanalyzer
flask run
```

## Conclusion
- The tool is under development. Connect with [us](mailto:nayan@crazyideas.co.in?subject=Contribute) to contribute.
- Powered by [Pycharm](https://www.jetbrains.com/?from=TPFAnalyzer)