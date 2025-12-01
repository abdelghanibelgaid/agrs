# Contributing to AGRS

First of all, thank you for your interest in improving **AGRS – Agricultural Remote Sensing Library**. Contributions of all kinds are welcome, including bug reports, documentation fixes, new features, or example notebooks.

This document explains how to get started and how to propose changes in a way that is easy to review and maintain.


## 1. Ways to contribute

You can support the project in many ways:

- **Report bugs** – anything that crashes, behaves incorrectly, or produces unexpected output.
- **Add or improve features** – pick something from the roadmap or suggest your own.
- **Enhance the documentation** – clarify the README, add usage guides, or refine docstrings.
- **Create examples and tutorials** – small, reproducible scripts for the `examples/` folder.

Not sure whether your idea fits the project’s scope? Open a GitHub issue and let’s discuss it before you start coding.


## 2. Getting started (local development)

1. **Fork** the repository on GitHub.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/<your-username>/agrs.git
   cd agrs
   ```

3. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # on Windows: .venv\Scripts\activate
   ```

4. Install AGRS in editable mode with development dependencies:

   ```bash
   pip install -e . -r requirements.txt
   ```

5. Verify that imports work:

   ```bash
   python -c "import agrs; print(agrs.__version__)"
   ```


## 3. Project structure (quick overview)

Key directories and files:

* `agrs/`

  * `client.py` – main user-facing API (`s2agc` client).
  * `indices.py` – built-in index formulas (NDVI, EVI, NDWI, NDMI, NBR, etc.).
  * `selection.py` – snapshot selection strategies (fractional, fixed date, dates, top-N cloud-free, all).
  * `aggregation.py` – field-level aggregation logic.
  * `utils.py` – clipping, geometry helpers, etc.
  * `config.py` – default indices, fractions, and configuration.
  * `sources/planetary_computer_source.py` – Sentinel-2 L2A access via Microsoft Planetary Computer.
* `examples/` – minimal, runnable usage examples.
* `README.md` – main documentation and quickstart.
* `CONTRIBUTING.md` – this file.
* `LICENSE`, `setup.py`, `pyproject.toml` – packaging and metadata.

If you add new modules or packages, please update imports and packaging configuration accordingly.


## 4. Coding guidelines

To keep the codebase consistent and maintainable:

* **Style**

  * Follow standard Python style (PEP 8) as much as possible.
  * Prefer clear, explicit names (`field_id`, `snapshot_strategy`, `return_mode`) over abbreviations.
  * Use type hints for public functions and methods where reasonable.

* **Docstrings**

  * Use short, informative docstrings:

    * What the function does.
    * Key parameters and return types.
    * Any assumptions (e.g. CRS, units for reflectance or NPK).

* **Indices & bands**

  * When adding new indices:

    * Implement them in `agrs.indices.compute_indices`.
    * Handle missing bands gracefully (only compute if required bands exist).
    * Use safe division (avoid crashes on zero / NaN).

* **Snapshot strategies**

  * If you propose a new strategy:

    * Implement it in `agrs.selection`.
    * Add a clear name and parameters.
    * Wire it into `s2agc.get_features` with a documented `snapshot_strategy` option.


## 5. Tests and examples

### Tests

If you add or change core functionality:

* Add or update **unit tests** (if a tests folder exists in the repo, or create a minimal one if not).
* Keep tests small, fast, and deterministic (no external network calls in unit tests).
* Use mock or synthetic data (e.g., tiny rasters or polygons) for RS-specific logic.

### Examples

For new behaviours or workflows:

* Add a short script under `examples/`, e.g.:

  * `examples/08_new_index_example.py`
  * `examples/09_new_snapshot_strategy.py`

* Examples should:

  * Be runnable with minimal setup.
  * Print a `DataFrame.head()` or a simple summary.
  * Demonstrate **one clear idea** per file.


## 6. Opening issues

Before opening a new issue, please:

1. Search existing issues to see if it has already been reported or discussed.

2. When opening a **bug report**, include:

   * AGRS version (`pip show agrs`).
   * Python version and OS.
   * A minimal code snippet that reproduces the issue.
   * Relevant traceback or error message.

3. For a **feature request**, describe:

   * The problem or use case (e.g. “phenology-aware indices for wheat”).
   * Any references or existing tools you are inspired by.
   * A rough idea of the API you expect (if you have one).


## 7. Pull request workflow

1. **Create a branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, commit with clear messages:

   ```bash
   git commit -m "Add NBR-based drought index" 
   ```

3. **Rebase** or merge `main` into your branch if needed to stay up to date.

4. Push your branch and open a **Pull Request**:

   * Clearly describe:

     * What you changed.
     * Why you changed it.
     * Any new APIs, flags, or behaviours.
   * Link to related issues if they exist.

5. Be prepared to iterate:

   * Maintainers may request adjustments for clarity, tests, or documentation.

---

Thank you for helping to build AGRS! Your contributions make it more useful for the agronomy, remote sensing, and ML communities. If you have any questions about how best to contribute, feel free to open a **Discussion** or an **Issue** on GitHub.
