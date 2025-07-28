# ⚠️ Important Notes for Reviewers and Judges

This project uses **Git LFS (Large File Storage)** to handle large dependencies like offline models and wheel files required for execution.

## ❗ Do NOT Use GitHub ZIP Download

If you download the project using the **"Download ZIP"** option on GitHub:

* 🔴 Large files (e.g., `.whl`, `.safetensors`) will **NOT** be included
* 🔴 Project will **fail to build** or execute correctly

## ✅ Proper Way to Clone

To ensure all required files are downloaded:

1. **Install Git LFS**:

   * [Download Git LFS](https://git-lfs.com)
   * Or on Windows via [Chocolatey](https://chocolatey.org):

     ```bash
     choco install git-lfs
     ```
   * Then run:

     ```bash
     git lfs install
     ```

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/Prem-Kumar-Dev/AIHROUND1B.git
   cd AIHROUND1B
   ```

3. **(Optional) Pull LFS files manually** (if you cloned earlier):

   ```bash
   git lfs pull
   ```

---

## 📦 Why Git LFS Was Used

Due to GitHub's 100MB file size limit, the following files are tracked with LFS:

* Offline Model: `model.safetensors` (\~127 MB)
* Offline Torch Wheel: `torch-2.5.1+cpu*.whl` (\~166 MB)

These files are essential for offline, self-contained Docker builds during the Adobe Hackathon.

---

If you encounter issues or missing files, please ensure you used Git LFS correctly.
For any help, contact me at: **\[krprem514@gmail.com]**
