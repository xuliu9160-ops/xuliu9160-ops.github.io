require 'yaml'
require 'json'

root = File.expand_path('..', __dir__)
data = {
  profile: YAML.load_file(File.join(root, '_data/profile.yml')),
  papers: YAML.load_file(File.join(root, '_data/papers.yml'))
}
puts JSON.generate(data)
