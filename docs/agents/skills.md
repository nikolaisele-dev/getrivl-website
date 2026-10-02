# Felles skills og roller

Arbeidsflyten er `docs/agents/sele-workflow.md` i produktrepoer og
`docs/contracts/sele-agent-operating-mode.md` i claude-infra. Les den før valg
av planlegging, review og tester. Løp A har det avtalte unntaket fra obligatorisk
reviewduo/TDD; B/C bruker Matt Pococks skills. Oppstrøms skillfiler endres ikke.

## Oppstart etter rolle

| Rolle | Les og bruk |
|---|---|
| Koordinator | ask-matt, grilling og domain-modeling; eksisterende mål/kø/beslutninger. Nye hull avklares, allerede avklarte oppgaver går videre. |
| Utfører | Avklart oppgave og akseptanse; implement/tdd for B/C, diagnosing-bugs ved feil. Nye produktuklarheter samles hos koordinator. |
| Reviewleder | code-review, fast diff/base og bestilling; separate parallelle Standards/Spec for B/C. |
| Standards- eller Spec-reviewer | code-review og kun tildelt akse; ingen ekstra reviewduo. |
| QA/driftsoperatør | Oppgavens akseptanse og relevante prosjekt-runbooks/gater. |

Last relevante fag-skills ved behov (design, RN/React, Supabase osv.), ikke hele
biblioteket. De gir fagkompetanse, ikke en ekstra konkurrerende arbeidsprosess
eller produksjonsfullmakt. Bruk writing-for-agents ved regelendring. Ved review
av endrede instrukser: sjekk noen få relevante scenarioer i eksisterende review
og skill tekstkontroll fra faktisk observert agentatferd.

Manglende slash-kommando er ikke manglende metode: les faktisk SKILL.md og
referanser. Coordinatorens grill-with-docs er grilling + domain-modeling.
Bekreft faktisk lastede skills ved dispatch/rollebytte; en oppført skill er
ikke bevis på bruk. Implementer starter ikke nytt intervju om arvede svar.

## Installasjon og kilde

Delt uendret installasjon ligger i `~/.agents/skills/<navn>`; Claude oppdager
samme filer gjennom `~/.claude/skills/<navn>`. Pin og SHA-256 for SKILL.md står i
`matt-pocock-skills.lock.json` ved siden av denne fila. Referansefiler verifiseres
mot samme oppstrøms commit når installasjonen endres. Ikke installer en parallell
Claude-plugin eller en andre kopi for samme skill. Andre installerte fag-skills
beholdes; låsen gjelder Matt-pakken, ikke hele maskinens skillinventar.

På ny maskin: installer låsens engineering/productivity-kataloger fra eksakt
commit og eksponer samme innhold til begge verktøy. Ved manglende nødvendige
skills: reparer installasjonen før dispatch, ikke påstå at navn alene er nok.
Denne utrullingen oppgraderer ingen modell eller produktets AI-integrasjon.

## Prosjektadaptere

Les `docs/agents/issue-tracker.md` for prosjektets eksisterende oppgavekø og
`docs/agents/domain.md` for domenedokumenter når de finnes. Opprett ikke en
parallell kø. RIVL-koordinator leser også
`docs/contracts/coordinator-operating-rhythm.md` ved overtakelse; Git-detaljer
står i `docs/contracts/agent-workflow.md`. KLASOs produktstatus eies fortsatt
av backend-repoets ROADMAP, og rettigheter avgjøres fortsatt i backend.
