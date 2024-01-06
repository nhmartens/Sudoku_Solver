import imageSolver
import os

if __name__ == "__main__":
    unsolvedPath = "./Unsolved_Sudokus"
    solvedPath = "./Solutions_Sudokus"
    

    allowed_extensions = ['.png', '.jpeg']

    # Filter Folder files for pngs and jpegs
    files = [f for f in os.listdir(unsolvedPath) if os.path.isfile(os.path.join(unsolvedPath, f)) and any(f.lower().endswith(ext) for ext in allowed_extensions)]
    
    
