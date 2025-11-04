# GitHub Upload Guide

This guide provides step-by-step instructions for uploading the Mininet/Ryu COMOSAT project to GitHub.

---

## Prerequisites

1. **Git installed** on your system
   - Check: `git --version`
   - Install: https://git-scm.com/downloads

2. **GitHub account** created
   - Sign up: https://github.com/signup

3. **Project cleaned** (remove unnecessary files)
   - See [Pre-Upload Checklist](#pre-upload-checklist) below

---

## Step 1: Prepare Local Repository

### Navigate to Project Directory

```bash
# Windows (PowerShell)
cd "C:\Users\ilora.maity\OneDrive - University of Luxembourg\W2_CPPSat\Journal\code\mininet_ryu_comosat"

# Linux/Mac
cd ~/path/to/mininet_ryu_comosat
```

### Initialize Git Repository

```bash
# Initialize repository
git init

# Configure Git (if not already done globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Create .gitignore

Create a `.gitignore` file to exclude unnecessary files:

```bash
# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Generated files
plots/*.png
results/*.json
topology/mininet_topology_data.json
orchestrator/simulation_metrics.json
matlab_export/*.asv

# MATLAB
*.asv
*.autosave

# Logs
*.log
*.out

# Jupyter
.ipynb_checkpoints/

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp
EOF
```

### Stage Files

```bash
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status
```

---

## Step 2: Create Initial Commit

```bash
# Create initial commit
git commit -m "Initial commit: COMOSAT Mininet/Ryu implementation

Features:
- MATLAB export module for topology data
- Mininet topology builder for SAGIN networks
- Ryu SDN controller with domain-based control
- Simulation orchestrator with metrics collection
- Visualization tools including emulation plots
- Docker support for containerized deployment
- Distributed VM setup support
- Comprehensive documentation

Components:
- Controller: Ryu SDN controller application
- Orchestrator: Time-slot simulation manager
- Topology: Custom Mininet topology builder
- Visualization: Plot generation and analysis tools
- MATLAB Export: Data export from simulation
- Docker: Containerized deployment configuration"
```

---

## Step 3: Create GitHub Repository

### Via GitHub Website

1. **Go to GitHub**: https://github.com/new

2. **Repository Settings**:
   - **Repository name**: `comosat-mininet-ryu` (or your preferred name)
   - **Description**: `COMOSAT implementation using Mininet/Ryu for SAGIN networks - SDN controller placement demonstration`
   - **Visibility**: 
     - ✅ **Public** (for open research/publication)
     - 🔒 **Private** (if preferred)
   - **DO NOT** initialize with README, .gitignore, or license (we have these already)

3. **Click "Create repository"**

---

## Step 4: Connect and Push

### Add Remote Repository

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/comosat-mininet-ryu.git

# Verify remote
git remote -v
```

### Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If you get "main branch doesn't exist", try:
git branch -M main
git push -u origin main

# Alternative: If main branch doesn't exist, use master:
git branch -M master
git push -u origin master
```

### Authentication

**If prompted for credentials:**
- **Personal Access Token** (recommended): 
  1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token with `repo` scope
  3. Use token as password when prompted

- **SSH Key** (alternative):
  ```bash
  # Generate SSH key
  ssh-keygen -t ed25519 -C "your.email@example.com"
  
  # Add to SSH agent
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_ed25519
  
  # Add public key to GitHub: Settings → SSH and GPG keys → New SSH key
  
  # Change remote to SSH
  git remote set-url origin git@github.com:YOUR_USERNAME/comosat-mininet-ryu.git
  ```

---

## Step 5: Verify Upload

### Check Repository

1. **Visit your repository**: `https://github.com/YOUR_USERNAME/comosat-mininet-ryu`

2. **Verify files**:
   - ✅ README.md present
   - ✅ Source code files present
   - ✅ Documentation files present
   - ✅ .gitignore present
   - ✅ No generated files (plots, results)

3. **Check README rendering**: Should display properly formatted

---

## Step 6: Add Repository Metadata

### Add Topics (Tags)

On GitHub repository page:
1. Click **⚙️ Settings** (gear icon)
2. Scroll to **Topics**
3. Add topics:
   - `sdn`
   - `mininet`
   - `ryu`
   - `sagin`
   - `controller-placement`
   - `satellite-networks`
   - `network-emulation`
   - `research`

### Add Description

Update repository description on main page:
```
COMOSAT implementation using Mininet/Ryu for SAGIN networks. SDN controller placement demonstration with dynamic topology management, hierarchical control, and empirical validation.
```

### Set Repository Website (Optional)

If you have a paper or project website:
1. Go to **Settings** → **Pages**
2. Enter website URL

---

## Step 7: Create Releases (Optional)

For version tracking:

```bash
# Create a tag for current version
git tag -a v1.0.0 -m "Initial release: COMOSAT Mininet/Ryu implementation"

# Push tags to GitHub
git push origin v1.0.0
```

On GitHub:
1. Go to **Releases** → **Draft a new release**
2. Select tag `v1.0.0`
3. Add release notes:
   ```
   Initial release of COMOSAT Mininet/Ryu implementation.
   
   Features:
   - MATLAB export module
   - Mininet topology builder
   - Ryu SDN controller
   - Visualization tools
   - Docker support
   ```

---

## Pre-Upload Checklist

### Files to Include ✅

- [ ] `README.md` - Main documentation
- [ ] `controller/comosat_controller.py` - Ryu controller
- [ ] `orchestrator/orchestrator.py` - Simulation orchestrator
- [ ] `topology/sagin_topology.py` - Topology builder
- [ ] `visualization/visualize_results.py` - Visualization tools
- [ ] `matlab_export/*.m` - MATLAB export scripts
- [ ] `experiments/*.sh`, `experiments/*.bat` - Execution scripts
- [ ] `docker-compose.yml`, `Dockerfile.*` - Docker configuration
- [ ] `requirements.txt` - Python dependencies
- [ ] `visualization/EMULATION_PLOTS_GUIDE.md` - Data collection guide
- [ ] `visualization/PLOT_SUGGESTIONS.md` - Plot recommendations
- [ ] `GITHUB_UPLOAD.md` - This file

### Files to Exclude ❌

- [ ] `plots/*.png` - Generated visualizations
- [ ] `results/*.json` - Generated metrics
- [ ] `topology/mininet_topology_data.json` - Generated topology (large)
- [ ] `orchestrator/simulation_metrics.json` - Generated metrics
- [ ] `__pycache__/` - Python cache
- [ ] `*.asv` - MATLAB autosave files
- [ ] `*.log` - Log files
- [ ] IDE configuration files (`.vscode/`, `.idea/`)

### Documentation Cleanup

- [ ] Remove redundant MD files (see list below)
- [ ] Keep only essential documentation
- [ ] Ensure README.md is comprehensive

### Code Quality

- [ ] Remove commented-out code
- [ ] Remove debug print statements (or use logging)
- [ ] Ensure consistent code formatting
- [ ] Add docstrings to functions

---

## Removing Redundant Files

Before uploading, consider removing these redundant documentation files (if consolidated in README.md):

- `START_HERE.md` (redundant with README)
- `QUICKSTART.md` (redundant with README)
- `QUICK_REFERENCE.txt` (redundant with README)
- `DOCKER_README.md` (can keep for detailed Docker info, or merge)
- `WINDOWS_DOCKER_GUIDE.md` (merge into README Docker section)
- `DISTRIBUTED_SETUP.md` (redundant with README)
- `SETUP_COMOSAT.md` (redundant with README)
- `NETWORK_TROUBLESHOOTING.md` (redundant with README troubleshooting)
- `ARCHITECTURE_EXPLANATION.md` (optional, can keep for detailed architecture)
- `IMPLEMENTATION_NOTES.md` (optional, keep if has technical details)
- `PUBLISH_TO_GITHUB.md` (replaced by this file)
- `GITHUB_GUIDELINES.md` (redundant with this file)
- `GITHUB_CHECKLIST.md` (redundant with this file)

**Recommendation**: Keep only:
- `README.md` (main documentation)
- `GITHUB_UPLOAD.md` (this file)
- `visualization/EMULATION_PLOTS_GUIDE.md` (specialized guide)
- `visualization/PLOT_SUGGESTIONS.md` (specialized guide)

---

## Post-Upload Tasks

### Update README Badges (Optional)

Add badges to README.md:

```markdown
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Ryu](https://img.shields.io/badge/ryu-SDN-orange.svg)](https://ryu-sdn.org/)
[![Mininet](https://img.shields.io/badge/mininet-2.3+-green.svg)](http://mininet.org/)
```

### Enable Issues (Optional)

1. Go to **Settings** → **Features**
2. Enable **Issues**
3. Create issue templates if desired

### Add License File

Create `LICENSE` file (e.g., MIT, Apache 2.0, or your preferred license).

---

## Troubleshooting

### "Permission Denied"

```bash
# Check SSH key setup
ssh -T git@github.com

# Or use HTTPS with token
git remote set-url origin https://github.com/YOUR_USERNAME/comosat-mininet-ryu.git
```

### "Large File" Error

If files are too large (>100MB):
- Remove large generated files from repository
- Add to `.gitignore`
- Use Git LFS for large binary files (if needed)

### "Branch Name Conflict"

```bash
# Rename branch
git branch -M main

# Or use master
git branch -M master
```

### "Remote Already Exists"

```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/comosat-mininet-ryu.git
```

---

## Best Practices

1. **Regular Commits**: Commit changes frequently with descriptive messages
2. **Branch Strategy**: Use branches for features/experiments
3. **Pull Requests**: Review code before merging to main
4. **Documentation**: Keep README.md up to date
5. **Releases**: Tag major versions for reference
6. **Issues**: Use GitHub Issues for bug tracking and feature requests

---

## Repository Structure After Upload

```
comosat-mininet-ryu/
├── README.md                    # Main documentation
├── .gitignore                   # Git ignore rules
├── LICENSE                      # License file (if added)
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker configuration
├── Dockerfile.ryu              # Ryu container
├── Dockerfile.mininet          # Mininet container
├── controller/
│   └── comosat_controller.py
├── orchestrator/
│   └── orchestrator.py
├── topology/
│   └── sagin_topology.py
├── visualization/
│   ├── visualize_results.py
│   ├── EMULATION_PLOTS_GUIDE.md
│   └── PLOT_SUGGESTIONS.md
├── matlab_export/
│   └── *.m
├── experiments/
│   └── *.sh, *.bat
└── GITHUB_UPLOAD.md            # This file
```

---

## Contact

For questions about uploading or repository management:
- GitHub Help: https://docs.github.com/
- Git Documentation: https://git-scm.com/doc

---

**Good luck with your GitHub upload! 🚀**

