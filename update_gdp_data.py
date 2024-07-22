name: Run Python Script

on:
  schedule:
    - cron: '0 * * * *'  # Adjust the cron schedule as needed
  workflow_dispatch:  # Allows manual triggering

jobs:
  run_script:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pandas requests

      - name: Run script
        run: python update_gdp_data.py

      - name: Commit and push changes
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add GDP2.csv
          git commit -m "Update GDP data" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
