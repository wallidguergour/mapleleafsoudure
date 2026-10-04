# Contrôles de contenu avant publication.
# Usage : bundle exec ruby _outils/verifier-contenu.rb
#
# 1. Chaque article de _posts/ déclare exactement une catégorie (« category »), parmi les piliers de _data/piliers.yml.
# 2. Aucune page indexable ne contient de marqueur « [[ ... ]] » (texte visible, hors commentaires HTML).
# 3. Aucune page en noindex dans sitemap.xml ni dans llms.txt.
# 4. Chaque bloc JSON-LD est du JSON valide et ne contient aucun marqueur « [[ ».
#
# Code de sortie : 0 si tout est conforme, 1 sinon.
require "yaml"
require "json"
require "date"
require "tmpdir"

racine = File.expand_path("..", __dir__)
Dir.chdir(racine)
problemes = []

# 1. Catégories des articles
piliers = YAML.safe_load(File.read("_data/piliers.yml")).map { |p| p["slug"] }
Dir.glob("_posts/**/*.{md,markdown,html}").sort.each do |fichier|
  texte = File.read(fichier, encoding: "utf-8")
  entete = texte[/\A---\s*\n(.*?)\n---/m, 1]
  if entete.nil?
    problemes << "#{fichier} : en-tête absent"
    next
  end
  donnees = YAML.safe_load(entete, permitted_classes: [Date, Time]) || {}
  if donnees.key?("categories")
    problemes << "#{fichier} : utiliser « category » (une seule), pas « categories »"
  end
  categorie = donnees["category"]
  if !categorie.is_a?(String) || !piliers.include?(categorie)
    problemes << "#{fichier} : category doit être l'une de #{piliers.join(', ')} (trouvé : #{categorie.inspect})"
  end
end

# Build dans un dossier temporaire
destination = Dir.mktmpdir("verif-site")
unless system("bundle", "exec", "jekyll", "build", "-q", "-d", destination, out: File::NULL, err: File::NULL)
  abort "ÉCHEC : le build Jekyll a échoué."
end

noindex = []
Dir.glob(File.join(destination, "**", "*.html")).sort.each do |fichier|
  html = File.read(fichier, encoding: "utf-8")
  url = "/" + fichier.delete_prefix(destination + "/").sub(/index\.html\z/, "")
  next if html.include?('http-equiv="refresh"') # pages de redirection

  est_noindex = html =~ /<meta name="robots" content="[^"]*noindex/
  noindex << url if est_noindex

  # 2. Marqueurs visibles sur une page indexable
  # Marqueur = « [[ texte ]] » avec espaces (ne confond pas les tableaux JavaScript [[a, b]])
  visible = html.gsub(/<!--.*?-->/m, "")
  marqueurs = visible.scan(/\[\[ [^\[\]]+ \]\]/)
  if !est_noindex && !marqueurs.empty?
    problemes << "#{url} : page indexable avec #{marqueurs.size} marqueur(s) [[ ... ]]"
  end

  # 4. JSON-LD
  visible.scan(%r{<script type="application/ld\+json">(.*?)</script>}m).each do |(bloc)|
    begin
      JSON.parse(bloc)
    rescue JSON::ParserError => e
      problemes << "#{url} : JSON-LD invalide (#{e.message[0, 80]})"
    end
    problemes << "#{url} : JSON-LD avec une valeur non confirmée [[ ... ]]" if bloc =~ /\[\[ [^\[\]]+ \]\]/
  end
end

# 3. Sitemap et llms.txt sans page noindex
sitemap = File.read(File.join(destination, "sitemap.xml"))
llms = File.read(File.join(destination, "llms.txt"))
noindex.each do |url|
  problemes << "sitemap.xml contient une page noindex : #{url}" if sitemap.include?("<loc>https://mapleleafsoudure.com#{url}</loc>")
  problemes << "llms.txt contient une page noindex : #{url}" if llms.include?("https://mapleleafsoudure.com#{url})")
end
problemes << "llms.txt contient un marqueur [[ ... ]]" if llms =~ /\[\[ [^\[\]]+ \]\]/

if problemes.empty?
  puts "OK : contenu conforme (catégories, marqueurs, sitemap, llms.txt, JSON-LD)."
  exit 0
else
  puts "À CORRIGER :"
  problemes.each { |p| puts "  - #{p}" }
  exit 1
end
