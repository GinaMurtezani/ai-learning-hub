from django.core.management.base import BaseCommand

from chat.models import ChatAgent
from core.models import Achievement
from lessons.models import Lesson, LearningPath

PATHS = [
    {
        "slug": "ai-grundlagen",
        "title": "AI Grundlagen",
        "description": "Lerne die Grundlagen der Künstlichen Intelligenz — von den Basics bis zu deinem ersten Prompt.",
        "icon": "\U0001F9E0",
        "difficulty": "beginner",
        "order": 1,
        "lessons": [
            {
                "slug": "was-ist-ki",
                "title": "Was ist K\u00fcnstliche Intelligenz?",
                "order": 1,
                "xp_reward": 10,
                "ai_system_prompt": (
                    "Du bist ein freundlicher AI-Tutor. Erkl\u00e4re Konzepte der "
                    "K\u00fcnstlichen Intelligenz auf einfache Art. Verwende Analogien "
                    "aus dem Alltag. Der Lernende ist Anf\u00e4nger."
                ),
                "content": """\
## Was ist K\u00fcnstliche Intelligenz?

K\u00fcnstliche Intelligenz (KI) ist ein Bereich der Informatik, der sich damit besch\u00e4ftigt, \
Maschinen F\u00e4higkeiten beizubringen, die normalerweise menschliche Intelligenz erfordern. \
Dazu geh\u00f6ren Dinge wie Sprache verstehen, Bilder erkennen, Entscheidungen treffen und \
aus Erfahrungen lernen.

### KI im Alltag

Du begegnest KI t\u00e4glich, oft ohne es zu merken:
- **Sprachassistenten** wie Siri oder Alexa verstehen deine Fragen
- **Empfehlungen** auf Netflix oder Spotify basieren auf KI-Algorithmen
- **Autokorrektur** auf deinem Smartphone nutzt KI
- **Navigation** in Google Maps berechnet optimale Routen mit KI

### Warum ist KI jetzt so wichtig?

Drei Faktoren haben den aktuellen KI-Boom ausgel\u00f6st:
1. **Mehr Daten** — Das Internet erzeugt riesige Datenmengen zum Trainieren
2. **Mehr Rechenleistung** — Moderne GPUs erm\u00f6glichen komplexe Berechnungen
3. **Bessere Algorithmen** — Durchbr\u00fcche wie Transformer-Architekturen (2017)
""",
            },
            {
                "slug": "wie-funktionieren-llms",
                "title": "Wie funktionieren Large Language Models?",
                "order": 2,
                "xp_reward": 10,
                "ai_system_prompt": (
                    "Du bist ein AI-Tutor der Large Language Models erkl\u00e4rt. "
                    "Verwende einfache Analogien. Erkl\u00e4re wie LLMs trainiert "
                    "werden und wie sie Text generieren."
                ),
                "content": """\
## Wie funktionieren Large Language Models?

Large Language Models (LLMs) wie Claude, GPT oder Gemini sind KI-Systeme, \
die auf riesigen Textmengen trainiert wurden. Ihr Kernprinzip ist \u00fcberraschend einfach: \
**Sie sagen das n\u00e4chste Wort vorher.**

### Training

Stell dir vor, du liest Millionen von B\u00fcchern, Webseiten und Artikeln. \
Irgendwann erkennst du Muster: Nach "Guten" kommt oft "Morgen", nach \
"K\u00fcnstliche" oft "Intelligenz". LLMs machen genau das — aber in einem \
viel gr\u00f6sseren Massstab und mit mathematischer Pr\u00e4zision.

### Tokens

LLMs lesen nicht buchstabenweise, sondern in **Tokens**. Ein Token ist \
ein Wortst\u00fcck — oft ein ganzes Wort, manchmal ein Wortteil:
- "Hallo" → 1 Token
- "K\u00fcnstliche Intelligenz" → 2-3 Tokens
- "Donaudampfschifffahrtsgesellschaft" → mehrere Tokens

### Vorhersage

Bei jeder Anfrage generiert das LLM Token f\u00fcr Token eine Antwort. \
Es berechnet Wahrscheinlichkeiten f\u00fcr jedes m\u00f6gliche n\u00e4chste Token und \
w\u00e4hlt eines aus. Dieser Prozess wiederholt sich, bis die Antwort vollst\u00e4ndig ist.
""",
            },
            {
                "slug": "tokens-kontext-temperatur",
                "title": "Tokens, Kontext und Temperatur",
                "order": 3,
                "xp_reward": 10,
                "ai_system_prompt": (
                    "Du bist ein AI-Tutor. Erkl\u00e4re die Konzepte Tokens, "
                    "Kontext-Fenster und Temperatur bei LLMs. Gib praktische Beispiele."
                ),
                "content": """\
## Tokens, Kontext und Temperatur

Drei Schl\u00fcsselkonzepte bestimmen, wie ein LLM arbeitet.

### Tokens — Die Bausteine

Tokens sind die Einheiten, in denen LLMs denken. Ein Token entspricht \
ungef\u00e4hr 3/4 eines englischen Wortes. Warum ist das wichtig?
- **Kosten** werden pro Token berechnet
- **Geschwindigkeit** h\u00e4ngt von der Token-Anzahl ab
- **Limits** begrenzen wie viel Text verarbeitet werden kann

### Kontext-Fenster (Context Window)

Das Kontext-Fenster ist das "Ged\u00e4chtnis" eines LLMs w\u00e4hrend eines Gespr\u00e4chs. \
Es bestimmt, wie viel Text das Modell gleichzeitig "sehen" kann:
- Claude: bis zu 200K Tokens (\u2248 150'000 W\u00f6rter)
- Das ist wie ein ganzes Buch auf einmal lesen k\u00f6nnen!

### Temperatur

Die Temperatur steuert die "Kreativit\u00e4t" der Antworten:
- **Temperatur 0** → Deterministisch, immer die wahrscheinlichste Antwort
- **Temperatur 0.5** → Ausgewogen zwischen Pr\u00e4zision und Kreativit\u00e4t
- **Temperatur 1.0** → Kreativer, aber weniger vorhersagbar

**Faustregel:** Niedrige Temperatur f\u00fcr Fakten, hohe f\u00fcr kreatives Schreiben.
""",
            },
            {
                "slug": "dein-erster-prompt",
                "title": "Dein erster Prompt",
                "order": 4,
                "xp_reward": 15,
                "ai_system_prompt": (
                    "Du bist ein AI-Tutor der beim Schreiben von Prompts hilft. "
                    "Gib konstruktives Feedback auf Prompt-Versuche und zeige wie "
                    "man sie verbessern kann."
                ),
                "content": """\
## Dein erster Prompt

Jetzt wird es praktisch! Ein guter Prompt ist wie eine gute Frage — \
je klarer du fragst, desto besser die Antwort.

### Die Grundregeln

1. **Sei spezifisch** — Statt "Erkl\u00e4r mir KI" besser "Erkl\u00e4re mir in 3 S\u00e4tzen, \
was der Unterschied zwischen Machine Learning und Deep Learning ist"
2. **Gib Kontext** — "Ich bin Anf\u00e4nger und m\u00f6chte..."
3. **Definiere das Format** — "Antworte als Aufz\u00e4hlung" oder "Schreibe maximal 100 W\u00f6rter"

### Beispiele

**Schwacher Prompt:**
> Was ist Machine Learning?

**Starker Prompt:**
> Erkl\u00e4re einem 15-J\u00e4hrigen in maximal 5 S\u00e4tzen, was Machine Learning ist. \
> Verwende eine Analogie aus dem Sport.

### Probier es aus!

Nutze den AI-Chat rechts, um deine ersten Prompts zu testen. \
Versuche verschiedene Formulierungen und beobachte, wie sich die Antworten \u00e4ndern.
""",
            },
        ],
    },
    {
        "slug": "prompt-engineering",
        "title": "Prompt Engineering",
        "description": "Lerne fortgeschrittene Techniken f\u00fcr effektive Prompts — von Few-Shot bis Chain-of-Thought.",
        "icon": "\u270D\uFE0F",
        "difficulty": "intermediate",
        "order": 2,
        "lessons": [
            {
                "slug": "klare-anweisungen",
                "title": "Klare Anweisungen formulieren",
                "order": 1,
                "xp_reward": 15,
                "ai_system_prompt": (
                    "Du bist ein Prompt Engineering Tutor. Hilf dem Lernenden "
                    "klare und pr\u00e4zise Anweisungen zu formulieren. Gib Feedback "
                    "zu Prompt-Versuchen."
                ),
                "content": """\
## Klare Anweisungen formulieren

Der wichtigste Skill im Prompt Engineering ist Klarheit. \
Ein LLM kann nicht Gedanken lesen — es braucht pr\u00e4zise Anweisungen.

### Die 4 Elemente eines guten Prompts

1. **Rolle** — Wer soll die KI sein? "Du bist ein erfahrener Python-Entwickler..."
2. **Aufgabe** — Was soll getan werden? "Schreibe eine Funktion die..."
3. **Kontext** — Welche Rahmenbedingungen? "F\u00fcr ein Django-Projekt mit PostgreSQL..."
4. **Format** — Wie soll die Antwort aussehen? "Gib den Code mit Kommentaren zur\u00fcck..."

### Spezifizit\u00e4t

Je spezifischer deine Anweisung, desto besser das Ergebnis:
- \u2718 "Mach es besser"
- \u2714 "Verbessere die Lesbarkeit durch k\u00fcrzere Funktionen (max. 20 Zeilen) und beschreibende Variablennamen"

### Negative Anweisungen

Manchmal hilft es zu sagen, was die KI NICHT tun soll:
- "Verwende keine externen Bibliotheken"
- "Antworte nicht mit Code, sondern erkl\u00e4re das Konzept"
""",
            },
            {
                "slug": "few-shot-prompting",
                "title": "Few-Shot Prompting",
                "order": 2,
                "xp_reward": 15,
                "ai_system_prompt": (
                    "Du bist ein Prompt Engineering Tutor. Erkl\u00e4re Few-Shot "
                    "Prompting und hilf dem Lernenden eigene Few-Shot Prompts "
                    "zu erstellen."
                ),
                "content": """\
## Few-Shot Prompting

Few-Shot Prompting bedeutet, dem LLM **Beispiele** zu geben, \
damit es das gew\u00fcnschte Muster erkennt.

### Zero-Shot vs. Few-Shot

**Zero-Shot** (ohne Beispiele):
> Klassifiziere die Stimmung: "Das Produkt ist fantastisch!"

**Few-Shot** (mit Beispielen):
> Klassifiziere die Stimmung als positiv, negativ oder neutral.
>
> "Das Essen war kalt" → negativ
> "Ganz okay, nichts Besonderes" → neutral
> "Absolut fantastisch!" → positiv
>
> "Das Produkt ist fantastisch!" →

### Wann Few-Shot nutzen?

- Bei speziellen Formaten oder Strukturen
- Wenn das LLM das gew\u00fcnschte Muster nicht von selbst erkennt
- Bei Klassifikationsaufgaben mit eigenen Kategorien

### Tipps

- **3-5 Beispiele** reichen meist aus
- Beispiele sollten **divers** sein (verschiedene F\u00e4lle abdecken)
- Beispiele sollten **konsistent** formatiert sein
""",
            },
            {
                "slug": "chain-of-thought",
                "title": "Chain-of-Thought",
                "order": 3,
                "xp_reward": 20,
                "ai_system_prompt": (
                    "Du bist ein Prompt Engineering Tutor. Erkl\u00e4re Chain-of-Thought "
                    "Prompting und zeige wie schrittweises Denken die Ergebnisse verbessert."
                ),
                "content": """\
## Chain-of-Thought Prompting

Chain-of-Thought (CoT) fordert das LLM auf, **Schritt f\u00fcr Schritt zu denken**, \
bevor es eine Antwort gibt.

### Warum funktioniert das?

LLMs machen weniger Fehler, wenn sie ihre "Gedanken" ausschreiben. \
Es ist wie bei Menschen: Wer eine Matheaufgabe im Kopf l\u00f6st, macht mehr \
Fehler als jemand, der den L\u00f6sungsweg aufschreibt.

### Einfaches CoT

F\u00fcge einfach hinzu: **"Denke Schritt f\u00fcr Schritt."**

> Ein Zug f\u00e4hrt um 9:00 los und braucht 2h 45min. Wann kommt er an?
> Denke Schritt f\u00fcr Schritt.

### Strukturiertes CoT

F\u00fcr komplexere Aufgaben:
> Analysiere das Problem in folgenden Schritten:
> 1. Identifiziere die gegebenen Informationen
> 2. Bestimme was gesucht ist
> 3. W\u00e4hle einen L\u00f6sungsansatz
> 4. F\u00fchre die L\u00f6sung durch
> 5. \u00dcberpr\u00fcfe das Ergebnis

### Wann CoT nutzen?

- Mathematische oder logische Probleme
- Mehrstufige Entscheidungen
- Komplexe Analysen
""",
            },
        ],
    },
    {
        "slug": "agentic-workflows",
        "title": "Agentic Workflows",
        "description": "Entdecke die Welt der AI Agents — von Tool Use \u00fcber Multi-Agent Systeme bis zu eigenen Workflows.",
        "icon": "\U0001F916",
        "difficulty": "advanced",
        "order": 3,
        "lessons": [
            {
                "slug": "was-sind-ai-agents",
                "title": "Was sind AI Agents?",
                "order": 1,
                "xp_reward": 20,
                "ai_system_prompt": (
                    "Du bist ein AI-Experte der Agentic AI erkl\u00e4rt. Der Lernende "
                    "kennt bereits LLM-Grundlagen und Prompt Engineering."
                ),
                "content": """\
## Was sind AI Agents?

Ein AI Agent ist ein LLM, das **autonom handeln** kann. \
W\u00e4hrend ein normaler Chatbot nur auf Fragen antwortet, kann ein Agent:
- **Entscheidungen treffen** \u00fcber n\u00e4chste Schritte
- **Tools verwenden** (Dateien lesen, APIs aufrufen, Code ausf\u00fchren)
- **Iterieren** bis eine Aufgabe erledigt ist

### Der Agent-Loop

```
Aufgabe → Denken → Handeln → Beobachten → Denken → ...
```

Ein Agent arbeitet in einer Schleife:
1. Er analysiert die Aufgabe
2. Er entscheidet welches Tool er braucht
3. Er verwendet das Tool
4. Er bewertet das Ergebnis
5. Er wiederholt oder liefert die Antwort

### Beispiele

- **Claude Code** — Ein Agent der Code schreiben, testen und debuggen kann
- **Devin** — Ein Agent der ganze Software-Projekte umsetzen kann
- **AutoGPT** — Ein fr\u00fcher experimenteller Agent
""",
            },
            {
                "slug": "tool-use-function-calling",
                "title": "Tool Use und Function Calling",
                "order": 2,
                "xp_reward": 20,
                "ai_system_prompt": (
                    "Du bist ein AI-Experte der Tool Use und Function Calling "
                    "erkl\u00e4rt. Gib praktische Beispiele mit der Anthropic API."
                ),
                "content": """\
## Tool Use und Function Calling

Tool Use gibt LLMs die F\u00e4higkeit, **externe Funktionen aufzurufen**. \
Das LLM generiert dabei nicht direkt eine Antwort, sondern einen \
strukturierten Funktionsaufruf.

### Wie funktioniert es?

1. Du definierst **Tools** mit Namen, Beschreibung und Parametern
2. Das LLM entscheidet, ob es ein Tool braucht
3. Es generiert einen **JSON-Funktionsaufruf**
4. Dein Code f\u00fchrt die Funktion aus
5. Das Ergebnis geht zur\u00fcck ans LLM

### Beispiel-Tool

```json
{
  "name": "get_weather",
  "description": "Gibt das aktuelle Wetter f\u00fcr einen Ort zur\u00fcck",
  "parameters": {
    "location": "string",
    "unit": "celsius | fahrenheit"
  }
}
```

### Typische Tools

- Datenbankabfragen
- API-Aufrufe
- Dateisystem-Operationen
- Web-Suche
- Code-Ausf\u00fchrung
""",
            },
            {
                "slug": "multi-agent-systeme",
                "title": "Multi-Agent Systeme",
                "order": 3,
                "xp_reward": 25,
                "ai_system_prompt": (
                    "Du bist ein AI-Experte der Multi-Agent Systeme erkl\u00e4rt. "
                    "Diskutiere Navigator/Builder Patterns und Agent-Orchestrierung."
                ),
                "content": """\
## Multi-Agent Systeme

Statt einem einzelnen Agent k\u00f6nnen **mehrere spezialisierte Agents** zusammenarbeiten.

### Warum mehrere Agents?

- **Spezialisierung** — Jeder Agent ist Experte f\u00fcr eine Aufgabe
- **Parallelisierung** — Agents k\u00f6nnen gleichzeitig arbeiten
- **Kontrolle** — Kleinere Agents sind einfacher zu steuern

### Architektur-Patterns

**Navigator/Builder Pattern:**
- Ein **Navigator-Agent** plant und koordiniert
- Mehrere **Builder-Agents** f\u00fchren spezifische Aufgaben aus

**Pipeline Pattern:**
- Agent A → Agent B → Agent C
- Jeder Agent verarbeitet und reicht weiter

**Hierarchisches Pattern:**
- Ein Supervisor delegiert an Sub-Agents
- Sub-Agents k\u00f6nnen eigene Sub-Agents haben

### Herausforderungen

- Kommunikation zwischen Agents
- Fehlerbehandlung und Recovery
- Kosten-Kontrolle (jeder Agent verbraucht Tokens)
""",
            },
            {
                "slug": "mcp-model-context-protocol",
                "title": "MCP \u2014 Model Context Protocol",
                "order": 4,
                "xp_reward": 25,
                "ai_system_prompt": (
                    "Du bist ein AI-Experte der MCP erkl\u00e4rt. Der Lernende hat "
                    "bereits MCP-Server eingerichtet (Jira, GitHub, Filesystem)."
                ),
                "content": """\
## MCP — Model Context Protocol

Das Model Context Protocol (MCP) ist ein **offener Standard** von Anthropic, \
der die Kommunikation zwischen AI-Anwendungen und Datenquellen standardisiert.

### Das Problem

Jede Integration (GitHub, Slack, Datenbank...) braucht eigenen Code. \
Bei N Anwendungen und M Datenquellen ergibt das N×M Integrationen.

### Die L\u00f6sung

MCP definiert ein **einheitliches Protokoll**:
- Jede Datenquelle implementiert einen **MCP-Server**
- Jede Anwendung implementiert einen **MCP-Client**
- Ergebnis: N+M Integrationen statt N×M

### MCP-Konzepte

- **Tools** — Funktionen die der Agent aufrufen kann
- **Resources** — Daten die der Agent lesen kann
- **Prompts** — Vordefinierte Prompt-Templates

### Beispiele f\u00fcr MCP-Server

- **Filesystem** — Dateien lesen und schreiben
- **GitHub** — Issues, PRs, Repos verwalten
- **Jira** — Tickets erstellen und bearbeiten
- **Slack** — Nachrichten senden und lesen
""",
            },
            {
                "slug": "eigene-workflows",
                "title": "Eigene Workflows bauen",
                "order": 5,
                "xp_reward": 30,
                "ai_system_prompt": (
                    "Du bist ein AI-Experte der beim Erstellen eigener AI-Workflows "
                    "hilft. Gib praktische Tipps und Architekturvorschl\u00e4ge."
                ),
                "content": """\
## Eigene Workflows bauen

Jetzt bist du bereit, eigene AI-Workflows zu erstellen!

### Workflow-Design

1. **Problem definieren** — Was soll automatisiert werden?
2. **Schritte identifizieren** — Welche Teilaufgaben gibt es?
3. **Tools w\u00e4hlen** — Welche Tools braucht der Agent?
4. **Fehlerf\u00e4lle planen** — Was passiert wenn etwas schiefgeht?

### Architektur-Entscheidungen

| Frage | Einfach | Komplex |
|---|---|---|
| Wie viele Schritte? | 1-3 | 5+ |
| Braucht es Tools? | Nein | Ja |
| Architektur | Single Prompt | Agent Loop |
| Fehlerbehandlung | Retry | Fallback Agent |

### Best Practices

- **Start simple** — Beginne mit einem einzelnen Prompt
- **Iteriere** — Verbessere schrittweise
- **Logge alles** — Speichere Inputs, Outputs und Entscheidungen
- **Setze Limits** — Max. Iterationen, Timeout, Token-Budget
- **Teste gr\u00fcndlich** — Edge Cases und Fehlerszenarios

### Dein erster Workflow

Probiere einen einfachen Workflow:
1. Nimm einen Text als Input
2. Lass ihn von Claude zusammenfassen
3. Lass die Zusammenfassung bewerten
4. Iteriere bis die Qualit\u00e4t stimmt
""",
            },
        ],
    },
    {
        "slug": "ai-in-finance",
        "title": "AI in Finance",
        "description": "Entdecke wie K\u00fcnstliche Intelligenz die Finanzwelt revolutioniert \u2014 von Risikobewertung bis algorithmischem Handel.",
        "icon": "\U0001F4B9",
        "difficulty": "intermediate",
        "order": 4,
        "lessons": [
            {
                "slug": "finance-ai-ueberblick",
                "title": "AI in der Finanzwelt \u2014 \u00dcberblick",
                "order": 1,
                "xp_reward": 15,
                "ai_system_prompt": (
                    "Du bist ein Finance-AI-Experte. Erkl\u00e4re wie KI in der "
                    "Finanzbranche eingesetzt wird. Verwende konkrete Beispiele "
                    "aus Banking, Versicherungen und Trading."
                ),
                "content": """\
## AI in der Finanzwelt

K\u00fcnstliche Intelligenz ver\u00e4ndert die Finanzbranche grundlegend. \
Von der Kreditvergabe bis zum Hochfrequenzhandel \u2014 AI-Systeme treffen \
heute Entscheidungen, die fr\u00fcher Wochen menschlicher Analyse erforderten.

### Einsatzgebiete

- **Kreditscoring** \u2014 AI bewertet Kreditw\u00fcrdigkeit in Sekunden
- **Betrugserkennung** \u2014 Anomalie-Erkennung in Echtzeit
- **Algorithmischer Handel** \u2014 Automatisierte Handelsstrategien
- **Robo-Advisors** \u2014 Automatisierte Anlageberatung
- **Risikomanagement** \u2014 Vorhersage von Marktrisiken

### Warum jetzt?

Drei Faktoren treiben die Transformation:
1. **Datenverf\u00fcgbarkeit** \u2014 Finanzdaten in Echtzeit
2. **Regulierung** \u2014 Neue Compliance-Anforderungen erfordern Automatisierung
3. **Wettbewerb** \u2014 FinTechs setzen AI-First-Strategien ein
""",
            },
            {
                "slug": "risikobewertung-ml",
                "title": "Risikobewertung mit Machine Learning",
                "order": 2,
                "xp_reward": 15,
                "ai_system_prompt": (
                    "Du bist ein Finance-AI-Experte f\u00fcr Risikobewertung. "
                    "Erkl\u00e4re ML-basierte Kreditscoring-Modelle und Risikoanalyse. "
                    "Verwende Beispiele aus der Praxis."
                ),
                "content": """\
## Risikobewertung mit Machine Learning

Traditionelle Kreditscoring-Modelle basieren auf wenigen Variablen. \
ML-Modelle k\u00f6nnen Hunderte von Merkmalen gleichzeitig analysieren.

### Traditionell vs. ML

| Aspekt | Traditionell | ML-basiert |
|---|---|---|
| Variablen | 10-20 | 100-500+ |
| Aktualisierung | J\u00e4hrlich | Kontinuierlich |
| Genauigkeit | Gut | Deutlich besser |
| Erkl\u00e4rbarkeit | Hoch | Herausfordernd |

### Feature Engineering

Typische Features f\u00fcr Kreditscoring:
- **Zahlungshistorie** \u2014 P\u00fcnktlichkeit, Ausf\u00e4lle
- **Kontoaktivit\u00e4t** \u2014 Transaktionsmuster, Saldi
- **Externe Daten** \u2014 Wirtschaftsindikatoren, Branchendaten

### Herausforderung: Fairness

ML-Modelle k\u00f6nnen bestehende Vorurteile verst\u00e4rken:
- **Bias in Trainingsdaten** \u2014 Historische Diskriminierung
- **Proxy-Variablen** \u2014 Postleitzahl als Proxy f\u00fcr Ethnie
- **L\u00f6sung:** Fairness-Metriken und regelm\u00e4ssige Audits
""",
            },
            {
                "slug": "algorithmischer-handel",
                "title": "Algorithmischer Handel",
                "order": 3,
                "xp_reward": 20,
                "ai_system_prompt": (
                    "Du bist ein Finance-AI-Experte f\u00fcr algorithmischen Handel. "
                    "Erkl\u00e4re Trading-Strategien und wie AI dabei eingesetzt wird. "
                    "Weise auf Risiken hin."
                ),
                "content": """\
## Algorithmischer Handel

Algorithmic Trading nutzt Programme, um Handelsentscheidungen \
automatisch zu treffen und auszuf\u00fchren.

### Strategien

**Trend-Following:**
- Erkennt Markttrends mit Moving Averages
- AI verbessert das Timing durch Pattern Recognition

**Mean Reversion:**
- Setzt darauf, dass Preise zum Durchschnitt zur\u00fcckkehren
- ML identifiziert optimale Ein- und Ausstiegspunkte

**Sentiment Analysis:**
- LLMs analysieren News und Social Media
- Stimmungsindikatoren beeinflussen Handelsentscheidungen

### Hochfrequenzhandel (HFT)

- Entscheidungen in **Mikrosekunden**
- Nutzt minimale Preisunterschiede
- Erfordert Co-Location bei B\u00f6rsen-Servern

### Risiken

- **Flash Crashes** \u2014 Algorithmen verst\u00e4rken sich gegenseitig
- **Overfitting** \u2014 Strategien funktionieren nur mit historischen Daten
- **Black Box** \u2014 Schwer nachvollziehbare Entscheidungen
""",
            },
            {
                "slug": "betrugserkennung",
                "title": "Betrugserkennung mit AI",
                "order": 4,
                "xp_reward": 20,
                "ai_system_prompt": (
                    "Du bist ein Finance-AI-Experte f\u00fcr Betrugserkennung. "
                    "Erkl\u00e4re Anomalie-Erkennung, regelbasierte vs. ML-Systeme "
                    "und Real-World-Beispiele."
                ),
                "content": """\
## Betrugserkennung mit AI

Finanzbetrug verursacht j\u00e4hrlich Milliardenverluste. \
AI-Systeme erkennen verd\u00e4chtige Muster in Echtzeit.

### Ans\u00e4tze

**Regelbasiert (traditionell):**
- "Transaktion > 10'000 CHF \u2192 Flaggen"
- Einfach, aber leicht zu umgehen

**Machine Learning:**
- Lernt normale Muster pro Kunde
- Erkennt Abweichungen automatisch
- Passt sich an neue Betrugsmuster an

### Typische Anomalien

- **Ungewohnter Standort** \u2014 Karte in zwei L\u00e4ndern gleichzeitig
- **Ungew\u00f6hnlicher Betrag** \u2014 Pl\u00f6tzlich hohe Transaktionen
- **Zeitmuster** \u2014 Transaktionen zu ungew\u00f6hnlichen Zeiten
- **Verhaltens\u00e4nderung** \u2014 Neue H\u00e4ndlerkategorien

### Challenge: False Positives

Das gr\u00f6sste Problem ist die Balance zwischen:
- **Erkennung** \u2014 M\u00f6glichst alle Betrugsf\u00e4lle finden
- **Pr\u00e4zision** \u2014 Legitime Transaktionen nicht blockieren
""",
            },
            {
                "slug": "llms-finanzanalyse",
                "title": "LLMs f\u00fcr Finanzanalyse",
                "order": 5,
                "xp_reward": 25,
                "ai_system_prompt": (
                    "Du bist ein Finance-AI-Experte f\u00fcr LLM-Anwendungen in der "
                    "Finanzanalyse. Erkl\u00e4re wie Claude und andere LLMs f\u00fcr "
                    "Finanzberichte, Sentiment-Analyse und Beratung genutzt werden."
                ),
                "content": """\
## LLMs f\u00fcr Finanzanalyse

Large Language Models er\u00f6ffnen v\u00f6llig neue M\u00f6glichkeiten \
f\u00fcr die Finanzanalyse.

### Anwendungen

**Dokumentenanalyse:**
- Gesch\u00e4ftsberichte automatisch zusammenfassen
- Risikofaktoren aus 10-K Filings extrahieren
- Regulatorische \u00c4nderungen tracken

**Sentiment-Analyse:**
- News und Earnings Calls analysieren
- Social-Media-Stimmung zu Aktien
- Analyst-Reports vergleichen

**Finanzberatung:**
- Individuelle Anlageempfehlungen
- Erkl\u00e4rung komplexer Finanzprodukte
- Portfolio-Review und Optimierung

### Prompt Engineering f\u00fcr Finance

```
Du bist ein Finanzanalyst. Analysiere den folgenden
Quartalsbericht und identifiziere:
1. Die 3 wichtigsten Kennzahlen
2. Risiken f\u00fcr das n\u00e4chste Quartal
3. Eine Einsch\u00e4tzung (bullish/bearish/neutral)

Begr\u00fcnde deine Einsch\u00e4tzung mit Zahlen aus dem Bericht.
```

### Grenzen

- **Keine Echtzeitdaten** \u2014 LLMs haben einen Wissensstichtag
- **Halluzinationen** \u2014 Erfundene Zahlen sind gef\u00e4hrlich
- **Keine Anlageberatung** \u2014 Regulatorische Grenzen beachten
""",
            },
        ],
    },
]

AGENTS = [
    {
        "slug": "general",
        "name": "AI Tutor",
        "description": "Allgemeiner AI-Tutor f\u00fcr alle Themen rund um K\u00fcnstliche Intelligenz.",
        "icon": "\U0001F916",
        "system_prompt": (
            "Du bist ein freundlicher und hilfreicher AI-Tutor auf der AI Learning Hub "
            "Plattform. Du hilfst Lernenden dabei, Konzepte der K\u00fcnstlichen Intelligenz "
            "zu verstehen. Antworte auf Deutsch, sei ermutigend und verwende einfache "
            "Erkl\u00e4rungen mit Beispielen."
        ),
        "color": "#00A76F",
    },
    {
        "slug": "finance",
        "name": "Finance AI",
        "description": "Spezialisierter Agent f\u00fcr AI-Anwendungen in der Finanzwelt.",
        "icon": "\U0001F4B9",
        "system_prompt": (
            "Du bist ein spezialisierter Finance-AI-Tutor. Du erkl\u00e4rst wie K\u00fcnstliche "
            "Intelligenz in der Finanzbranche eingesetzt wird: Risikobewertung, "
            "algorithmischer Handel, Betrugserkennung, Robo-Advisors und Finanzanalyse. "
            "Antworte auf Deutsch. Verwende praxisnahe Beispiele aus Banking, "
            "Versicherungen und Trading. Weise bei Anlageempfehlungen immer darauf hin, "
            "dass dies keine echte Finanzberatung ist."
        ),
        "color": "#FFC107",
    },
]

ACHIEVEMENTS = [
    {
        "slug": "first-lesson",
        "name": "Erste Schritte",
        "icon": "\U0001F3AF",
        "description": "Schliesse deine erste Lektion ab",
        "requirement_type": "lessons_completed",
        "requirement_value": 1,
        "xp_reward": 20,
    },
    {
        "slug": "first-chat",
        "name": "Erste Frage",
        "icon": "\U0001F4AC",
        "description": "Stelle deine erste Frage an den AI-Tutor",
        "requirement_type": "first_chat",
        "requirement_value": 1,
        "xp_reward": 15,
    },
    {
        "slug": "three-streak",
        "name": "Auf Kurs",
        "icon": "\U0001F525",
        "description": "Lerne 3 Tage hintereinander",
        "requirement_type": "streak",
        "requirement_value": 3,
        "xp_reward": 30,
    },
    {
        "slug": "all-basics",
        "name": "Grundlagen-Meister",
        "icon": "\U0001F9E0",
        "description": "Schliesse alle AI Grundlagen Lektionen ab",
        "requirement_type": "lessons_completed",
        "requirement_value": 4,
        "xp_reward": 50,
    },
    {
        "slug": "xp-100",
        "name": "Centurion",
        "icon": "\u26A1",
        "description": "Sammle 100 XP",
        "requirement_type": "xp_total",
        "requirement_value": 100,
        "xp_reward": 25,
    },
]


class Command(BaseCommand):
    help = "Seed learning paths, lessons, and achievements"

    def handle(self, *args, **options):
        # Clear existing data
        Lesson.objects.all().delete()
        LearningPath.objects.all().delete()
        Achievement.objects.all().delete()

        # Seed learning paths and lessons
        lesson_count = 0
        for path_data in PATHS:
            lessons_data = path_data.pop("lessons")
            path = LearningPath.objects.create(**path_data)
            for lesson_data in lessons_data:
                Lesson.objects.create(path=path, **lesson_data)
                lesson_count += 1
            # Restore for re-runnability within same process
            path_data["lessons"] = lessons_data

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(PATHS)} learning paths with {lesson_count} lessons"
            )
        )

        # Seed achievements
        for ach_data in ACHIEVEMENTS:
            Achievement.objects.create(**ach_data)

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(ACHIEVEMENTS)} achievements")
        )

        # Seed chat agents
        ChatAgent.objects.all().delete()
        for agent_data in AGENTS:
            ChatAgent.objects.create(**agent_data)

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(AGENTS)} chat agents")
        )
