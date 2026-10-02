# Sele — felles arbeidsflyt for agenter

## Autoritet og oppstart

Dette er Nikolais felles arbeidsavtale for eksisterende og nye prosjekter,
uavhengig av Claude Code, Codex/GPT, Cursor eller Conductor. Canonical er
`claude-infra/docs/contracts/sele-agent-operating-mode.md`; prosjektets
`docs/agents/sele-workflow.md` er en distribuert kopi. På Nikolais maskin
installeres samme innhold i `~/.agents/sele-workflow.md`.

Les denne avtalen, repoets `AGENTS.md` og `docs/agents/skills.md` ved oppstart
og gjenopptakelse. Velg oppgaven ut fra brukerens siste mål og gjeldende STOPP.
Bekreft rolle, kilde og faktisk lastede skills kort ved overtakelse/dispatch.

Denne avtalen erstatter eldre generelle plan-, review-, fulltest- og
avslutningsritualer. Produktkrav, datavern, sikkerhet og prosjektspesifikke
produksjonsfullmakter består. RIVLs stående DB-fullmakt gjelder bare RIVL;
KLASOs krav om eksplisitt godkjenning gjelder fortsatt KLASO. En CI-skip er
aldri en produksjonsfullmakt. Brukerens uttrykkelige instrukser går foran
skill-veiledning; gjenbruk godkjenning for samme avgrensede handling.

## Velg kontroll etter påvirkning

Skriv én kort begrunnelse i eksisterende oppgave/PR: hva endres, hvem/hva
påvirkes, hvilke kontroller gir bevis. Filendelse og antall linjer er ikke
risiko. Kombinerte eller uklare endringer får det bredeste relevante løpet.

| Løp | Avgrensning | Arbeid og review | Verifikasjon |
|---|---|---|---|
| A — innhold | Korrektur, interne forklaringer, statisk tekst/bilder eller layout med dokumentert fravær av funksjons-, rettighets- eller kontraktsendring | Én utfører med dokumentert egenkontroll; ingen obligatorisk agentduo, ny lang spec eller underoppgaver | Diff og relevante lenker/struktur; visning/rendering av berørte flater når brukeren ser endringen |
| B — avgrenset produkt | Isolert feilretting, lokal UI-atferd eller refaktorering med kjente konsumenter | Avklart kort oppgave; Matts implement/tdd og uavhengig Standards + Spec på endret innhold | Berørte atferdstester, typer og faktisk brukerflyt; bredere ved felles avhengigheter |
| C — delt/høy påvirkning | Delte komponenter, auth, data, backend, betaling, legal betydning, prompts/flagg, dependencies, CI, agentregler eller produksjonsrunbooks | Matts relevante plan-/implementeringsflyt og uavhengig Standards + Spec; eksisterende produksjonsgater | Kontroller for berørte konsumenter og kontrakter, bred suite der påvirkningen krever det, nødvendig runtime/readback |

A er et uttrykkelig unntak fra Matts obligatoriske to-akse-review og TDD for
endringer uten ny atferd. Utføreren kontrollerer fortsatt både samsvar med
bestillingen og relevante standarder. Ved tvil velges B/C; kall ikke eget
arbeid uavhengig review. Produktlogikk krever ikke automatisk hele økosystemets
suite, men endret felles grunnlag må kontrolleres hos konsumentene.

Praktiske grenser:
- Oversettelser: nøkler, variabler, fallback og plass kontrolleres på endrede
  språk. Nytt språk, datoformat, språkvalg eller lagring er B/C.
- Lokal stil/PDF-layout: kontroller faktiske tilstander, kontrast, tekstskalering,
  lange data og sideskift etter relevans. Beregning, tilgang, datafelter,
  trykkflate, fokus, animasjon og delt renderer/designsystem er B/C.
- Legal korrektur følger fortsatt canonical, nødvendig godkjenning og sync.
  Endret betydning, samtykke, metadata eller privacy-manifest er C.
- Hjelpetekst med nye helse-, pris- eller produktløfter må vurderes som C.
  Coach-prompt, terskel, retry og funksjonsflagg er funksjonalitet.
- Arrangement-/kataloginnhold valideres mot kilde og skjema. Krever publisering
  DB-migrasjon, består review/apply/readback selv om kilden er JSON.
- QA-bevis kontrolleres for kilde og sporbarhet. Endret akseptanse eller
  kontrakt er C. Tester/mocks/fixtures er B/C når beskyttelse kan påvirkes.

## Fra bestilling til ferdig

Koordinatoren avklarer nye produktbeslutninger med grilling + domain-modeling;
gjenbruk tidligere svar. Rutinemessige tekniske valg avgjøres innenfor oppdraget.
En liten avklart oppgave utføres i samme kontekst uten en egen spec-/ticketserie.
Flerøktsarbeid bruker to-spec/to-tickets med små komplette leveranser og bare
reelle avhengigheter. Bruk prosjektets eksisterende kø, ikke en ny parallell kø.

Én eier følger leveransen gjennom implementering, kontroll, PR, grønn relevant
CI, merge, nødvendig aktivering og faktisk akseptanse. Vanlige autoriserte
Git-steg trenger ikke gjentatt godkjenning. Behold PR per sammenhengende
leveranse/per repo; direkte push til main innføres ikke. Samle beslektet
korrektur når det passer; hold uavhengige produktendringer adskilt.

Ferdig betyr at avtalt resultat er tilgjengelig og kontrollert der det skal
brukes. Intern dokumentasjon trenger ikke app-QA eller nytt nativebygg.
Brukerinnhold i appen er ikke levert bare fordi kildekoden er merget. Bevar
avtalte språk, app/web-paritet og eventuell fysisk QA. Meld manglende bevis som
NOT RUN; behold overordnet produktoppgave åpen når akseptanse gjenstår.

Oppdater eksisterende roadmap når produktstatus faktisk endres, QA-matrise
når brukerobserverbar atferd endres, og eksisterende kort med bevislenker.
Ingen nye statuslogger eller avslutningsskript av vane. Sluttrapport: resultat,
relevante kontroller og konkret rest. Svar på norsk når Nikolai skriver norsk.

## Ressurser, CI og gjenbruk

Hold PR som draft under arbeid. Kjør målrettede tester og review lokalt. Når
kilden og basen er en moden kandidat, bruk `scripts/ci/submit-candidate.py`
med de reviewede `--expected-head` og `--expected-base` SHA-ene og `--workflow`
for hver tung kandidat-workflow i `.github/workflows/`. Den kontrollerer lokal
HEAD, åpen PR og fjern SHA-par. Hver tung workflow skal sette `run-name` til
`candidate head=<head SHA> base=<base SHA>` fra PR-eventens SHA-er; hjelperen
bruker kjøringens uforanderlige `head_sha` og `display_title` for å unngå
duplikatkjøring. GitHubs `pull_requests[].head/base` på gamle kjøringer kan
endre seg og er ikke kandidatbevis. Ved gammel kjøring med samme head uten
fingeravtrykk stopper hjelperen for CI-eierens kontroll. Den sender
`ready_for_review` (ved behov via draft). Ny kilde eller base krever ny review
og innsending. Et draft-/sync-steg
gir ikke tung CI eller et grønt required check. Ved delvis, kansellert eller
feilet kjøring undersøker CI-eieren årsaken og starter relevant kjøring
eksplisitt; manuelt `workflow_dispatch` er en reservevei.

Én CI-eier følger alle relevante required og rådgivende sjekker og logger,
dokumenterer feil og løsning på samme oppgave/PR, og verifiserer endelig kilde-
og base-SHA før merge. Daglig `main`-kjøring dekker integrasjon uten full suite
ved hvert main-push. Behold eksisterende sjekknavn og beskyttelsesgater.

Før første produksjonsaktivering fastsettes en release-SHA og gjennomføres en
uavhengig helkodegjennomgang, DB-/RLS-kontroll, ende-til-ende-test av kritiske
flyter og fysisk QA på native enhet der appen krever det. Knytt funn og bevis
til samme release-SHA; en endret SHA eller base krever ny vurdering av berørt
bevis før akseptanse.

Én integrator og én CI-eier; unngå samtidige fullsuiter/Docker-stakker på samme
maskin. Utdaterte testkjøringer kan kanselleres; produksjonsoperasjoner følger
sin runbook. Bruk varsler eller avgrenset oppfølging fremfor pollingløkker.

Gjenbruk bevis bare for uendret innhold med relevant kilde, base, konfigurasjon
og miljø. En gammel grønn SHA beviser ikke en ny kombinasjon. Gjenta etter
endring, feil eller konkret usikkerhet; når nødvendige kontroller er grønne,
gå videre til akseptanse. Diagnostiser feil og rett innen scope; en vilkårlig
retrygrense er verken stoppgrunn eller lov til å sende rødt arbeid.

Required checks skal rapportere riktig på sluttkandidaten. Innsnevring skjer
med reviewet CI-utvalg, aldri manuell omgåelse. Ukjent påvirkning faller tilbake
til bred kontroll. En filbane-klassifikator velger CI-arbeid, ikke reviewnivå;
agenten vurderer innholdet selv. Sikkerhetsskann og nødvendige drift-/kontrakt-
kontroller beholdes. Endring av beskyttede GitHub-innstillinger krever oppdrag.

## Kontekst, overtakelse og STOPP

Bruk underagenter bare når avgrenset arbeid sparer nok tid/kontekst til å
forsvare oppstart og integrasjon. Gi rolle, kilde, scope, arvede beslutninger,
skills og akseptanse; krev kort resultat med bevis. Forelder integrerer og
beholder ansvar. Følg avtalte modeller, kvote, synlighet og workerbudsjett;
underagenter omgår ingen av disse. Én reviewakse starter ikke nye reviewpar.

Ved fasegrense brukes ask-matt/PHASE-BOUNDARIES.md: fortsett når konteksten er
nyttig, skill ut en avgrenset oppgave ved gevinst, compact/handoff når grensen
krever det. Overlever mål, beslutninger, eksakt kilde, dirty arbeid, bevis,
prosesser, neste akseptansegate og eier. Skill ordre fra historikk/referanser.

En brukerSTOPP eller kvotepause stopper nye oppgaver og releasesteg, også hos
underagenter. Bevar nærmeste sikre punkt; fullfør bare runbooken for en allerede
pågående produksjonsoperasjon til kjent tilstand. Grønn CI, peer-GO eller ledig
kvote opphever ikke pausen. Ved gjenopptakelse fortsetter neste uferdige gate.

Hvis en regel faktisk stopper autorisert arbeid: pek på nøyaktig fil, siter
regelen og forklar hva som mangler. Skill uttrykkelig krav fra egen tolkning.
