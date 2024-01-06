import imageSolver
import os

if __name__ == "__main__":
    unsolvedPath = "./Unsolved_Sudokus"
    solvedPath = "./Solutions_Sudokus"
    

    allowedExtensions = ['.png', '.jpeg']

    # Filter Folder files for pngs and jpegs
    unsolvedFiles = [f for f in os.listdir(unsolvedPath) if os.path.isfile(os.path.join(unsolvedPath, f)) and any(f.lower().endswith(ext) for ext in allowedExtensions)]
    solvedFiles = [f.replace("solution_", "") for f in os.listdir(solvedPath) if os.path.isfile(os.path.join(solvedPath, f)) and any(f.lower().endswith(ext) for ext in allowedExtensions)]
    
    filesToSolve = [f for f in unsolvedFiles if f not in solvedFiles]
    
    for file in filesToSolve:
        filePath = os.path.join(unsolvedPath, file)
        imageSolver.solveImage(filePath)
        
