# Sentry-AI Manual Testing Checklist

This checklist contains tests that require manual execution.

## Instructions

1. Start Sentry-AI in a separate terminal: `make run`
2. For each test below, follow the steps and observe behavior
3. Mark the checkbox when complete
4. Note any issues in the "Notes" section

---

## Test 1: finder_delete_confirmation

- [ ] **Completed**

**App:** Finder  
**Type:** confirmation  

**Description:**  
Test file deletion confirmation

**Expected Behavior:**  
Sentry-AI should require confirmation for destructive actions

**Steps:**
1. Create test file
2. Move to Trash
3. Empty Trash
4. Observe confirmation dialog

**Notes:**

_[Add your observations here]_

---

## Test 2: safari_download_dialog

- [ ] **Completed**

**App:** Safari  
**Type:** dialog  

**Description:**  
Test download confirmation

**Expected Behavior:**  
Sentry-AI handles download confirmation

**Steps:**
1. Open Safari
2. Initiate file download
3. Observe download dialog

**Notes:**

_[Add your observations here]_

---

## Test 3: system_update_notification

- [ ] **Completed**

**App:** System Preferences  
**Type:** notification  

**Description:**  
Test system update notification

**Expected Behavior:**  
Should be blacklisted (no automation)

**Steps:**
1. Wait for system update notification
2. Observe Sentry-AI decision

**Notes:**

_[Add your observations here]_

---

## Test 4: performance_cpu_usage

- [ ] **Completed**

**App:** Activity Monitor  
**Type:** performance  

**Description:**  
Monitor CPU usage during operation

**Expected Behavior:**  
CPU usage should be < 5% average

**Steps:**
1. Open Activity Monitor
2. Run Sentry-AI for 5 minutes
3. Check CPU usage

**Notes:**

_[Add your observations here]_

---

## Test 5: performance_memory_usage

- [ ] **Completed**

**App:** Activity Monitor  
**Type:** performance  

**Description:**  
Monitor memory usage

**Expected Behavior:**  
Memory usage should be < 200 MB

**Steps:**
1. Check initial memory
2. Run for 30 minutes
3. Check memory growth

**Notes:**

_[Add your observations here]_

---

## Test 6: multi_app_switching

- [ ] **Completed**

**App:** Multiple  
**Type:** dialog  

**Description:**  
Test rapid app switching

**Expected Behavior:**  
Sentry-AI correctly identifies and handles each app

**Steps:**
1. Open TextEdit, Notes, Safari
2. Switch between apps rapidly
3. Trigger dialogs in each

**Notes:**

_[Add your observations here]_

---

