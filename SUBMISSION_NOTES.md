# GitHub Submission Notes

This folder is the GitHub-ready version of the Mountain Wellness project.

It preserves the original analytical work and adds a lightweight reproducibility/dashboard layer.

Included:

- final report PDF;
- raw Guarda and Vila Real weather datasets;
- original Orange workflows;
- generated report figures;
- original Python validation/model figure script;
- OK-day modelling datasets and Orange model flows;
- supplementary Python pipeline;
- processed dashboard-ready datasets;
- Streamlit dashboard;
- concise LaTeX report draft;
- README, asset manifest, and dependency file.

Intentionally excluded:

- old duplicate milestone drafts;
- unrelated example PDFs;
- zip archives;
- cache folders;
- macOS metadata files.

Recommended GitHub repository name:

```text
weather-based-wellness-retreat-site-selection
```

Main review path:

```text
1. Read reports/Report.pdf
2. Inspect project_work/Group06_Milestone3/
3. Inspect project_work/modeling/
4. Run the supplementary dashboard if desired
```

Main commands:

```bash
python src/build_analysis.py
streamlit run dashboard/streamlit_app.py
```
