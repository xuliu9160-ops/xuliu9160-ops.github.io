# Jiaxu Liu — Academic Website

Personal academic website built with Academic Pages and Jekyll.

Website: https://xuliu9160-ops.github.io/

## Update content

- `_data/profile.yml`: education, GPA, research experience, and honors.
- `_data/papers.yml`: accepted papers and manuscripts.
- `_pages/about.html`: biography.
- `images/portrait.jpg`: profile photo.
- `assets/css/custom.css`: visual refinements.

The About, Research, Publications, and CV pages reuse these data files. Committing to main triggers the GitHub Pages deployment workflow.

## Local development

With Ruby 3.3 installed, run `bundle install`, then `bundle exec jekyll serve`.

Based on [Academic Pages](https://github.com/academicpages/academicpages.github.io). Original template license retained.
