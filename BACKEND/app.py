from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import torchvision.models as models
import pymysql
from flask_cors import CORS
import nltk
from fuzzywuzzy import process

# Download NLP resources if needed
nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# ✅ Load Trained Model
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = torch.nn.Linear(model.fc.in_features, 3)

try:
    model.load_state_dict(torch.load("elephant_model.pth", map_location=torch.device("cpu")))
    model.eval()
except Exception as e:
    print(f"Error loading model: {e}")

# ✅ Connect to MySQL Database
conn = None
cursor = None
try:
    conn = pymysql.connect(host='localhost', user='Yuva', password='Yuva_06', database='image_bot')
    cursor = conn.cursor()
except Exception as e:
    print(f"Database connection error: {e}")

# ✅ Image Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # Normalization
])

# ✅ API: Analyze Elephant Image
@app.route("/analyze_elephant", methods=["POST"])
def analyze_elephant():
    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file uploaded or empty file"}), 400

    try:
        file = request.files["file"]
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
    except Exception as e:
        return jsonify({"error": f"Invalid image file: {str(e)}"}), 400

    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)
        predicted_class = output.argmax(dim=1).item()

    class_labels = ["African Bush Elephant", "African Forest Elephant", "Asian Elephant"]
    species = class_labels[predicted_class]

    return jsonify({"species": species})

# ✅ API: Query Elephant Data
@app.route('/query_species', methods=['GET'])
def query_species():
    species = request.args.get('species', '').strip()
    query = request.args.get('query', '').strip()

    if not species:
        return jsonify({"error": "No species provided"}), 400
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # ✅ Fetch Species Data
    if cursor:
        cursor.execute("SELECT * FROM elephant_species WHERE SPECIES_NAME = %s", (species,))
        result = cursor.fetchone()
    else:
        return jsonify({"error": "Database connection issue"}), 500

    if not result:
        return jsonify({"error": "Species not found in database"}), 404

    # ✅ Mapping Table Columns to JSON Keys
    elephant_data = {
        "species": result[1],
        "scientific_name": result[2],
        "habitat": result[3],
        "size": result[4],
        "weight": result[5],
        "diet": result[6],
        "lifespan": result[7],
        "population_estimate": result[8],
        "conservation_status": result[9],
        "geographical_distribution": result[10]
    }

    # ✅ Define Query Fields for Fuzzy Matching
    fields = {
        "scientific name": "scientific_name",
        "habitat": "habitat",
        "size": "size",
        "weight": "weight",
        "diet": "diet",
        "lifespan": "lifespan",
        "population": "population_estimate",
        "conservation status": "conservation_status",
        "geographical distribution": "geographical_distribution"
    }

    # ✅ Match User Query with Field
    best_match = process.extractOne(query, list(fields.keys()))
    if best_match and best_match[1] > 60:  # Matching confidence threshold
        matched_field = fields[best_match[0]]
        answer = elephant_data.get(matched_field, "Information not available")
        return jsonify({"field": best_match[0], "answer": answer})
    else:
        return jsonify({"error": "Could not interpret query. Please ask about habitat, diet, etc."}), 400

if __name__ == "__main__":
    app.run(debug=True)
