import os

def traverse_folders(folder):
    findings = []
    for dates in os.listdir(folder):
        for h_m_s in os.listdir(os.path.join(folder,dates)):
            findings.append([dates, h_m_s])
    return findings
