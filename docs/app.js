const $ = id => document.getElementById(id);
const storageKey = 'smart-internship-applications-v1';
let offers = [];
let applications = JSON.parse(localStorage.getItem(storageKey) || '[]');
const percent = n => `${Math.round(n * 100)} %`;
const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const save = () => localStorage.setItem(storageKey, JSON.stringify(applications));
function renderOffers() {
  const filtered = offers.filter(o => o.score >= Number($('filter').value));
  $('offers').innerHTML = filtered.length ? filtered.map(o => `<article class="offer"><div><h3>${escapeHtml(o.title)}</h3><p>${escapeHtml(o.company || 'Entreprise non indiquée')} · ${escapeHtml(o.location || 'Lieu non indiqué')}</p><div class="skills"><b>Acquises :</b> ${escapeHtml((o.matched || []).join(', ') || 'aucune')}<br><em>À développer :</em> ${escapeHtml((o.gaps || []).join(', ') || 'aucune')}</div>${o.url && /^https?:\/\//.test(o.url) ? `<p><a href="${escapeHtml(o.url)}" target="_blank" rel="noopener noreferrer">Voir l’offre ↗</a></p>` : ''}</div><span class="badge">${percent(o.score)}</span></article>`).join('') : '<p>Aucune offre pour ce filtre.</p>';
}
function renderApplications() {
  const sent = applications.length;
  const answered = applications.filter(a => a.status !== 'Envoyée').length;
  $('sent').textContent = sent;
  $('response-rate').textContent = sent ? percent(answered / sent) : '—';
  $('applications').innerHTML = sent ? applications.map((a, i) => `<tr><td>${escapeHtml(a.title)}</td><td>${escapeHtml(a.date)}</td><td><select data-status="${i}">${['Envoyée','Réponse reçue','Entretien','Refus','Acceptée'].map(s => `<option ${a.status === s ? 'selected' : ''}>${s}</option>`).join('')}</select></td><td><button class="secondary" data-remove="${i}">Supprimer</button></td></tr>`).join('') : '<tr><td colspan="4">Aucune candidature enregistrée.</td></tr>';
}
function renderData(data) {
  offers = data.offers || [];
  $('n-offers').textContent = offers.length;
  const scores = offers.map(o => o.score).sort((a,b) => a-b);
  $('median').textContent = scores.length ? percent((scores[Math.floor((scores.length-1)/2)] + scores[Math.floor(scores.length/2)]) / 2) : '—';
  $('high').textContent = offers.filter(o => o.score >= .7).length;
  $('updated').textContent = data.generated_at ? `Actualisé : ${new Date(data.generated_at).toLocaleDateString('fr-FR')}` : '';
  $('sources').textContent = `${offers.length} France Travail`;
  $('compensation').textContent = `${data.n_offers_with_compensation || 0} / ${offers.length}`;
  $('empty-skills').textContent = offers.filter(o => !o.required_skills?.length).length;
  const gaps = data.top_skill_gaps || [];
  $('gaps').innerHTML = gaps.length ? gaps.slice(0, 7).map(g => `<div class="bar"><div class="bar-label"><span>${escapeHtml(g.skill)}</span><b>${g.count}</b></div><div class="track"><div class="fill" style="width:${100*g.count/gaps[0].count}%"></div></div></div>`).join('') : '<p>Aucun écart disponible.</p>';
  $('application-offer').innerHTML = offers.length ? offers.map(o => `<option value="${escapeHtml(o.id)}">${escapeHtml(o.title)} · ${escapeHtml(o.company || '')}</option>`).join('') : '<option value="">Aucune offre disponible</option>';
  renderOffers();
}
$('filter').addEventListener('change', renderOffers);
$('application-date').value = new Date().toISOString().slice(0,10);
$('application-form').addEventListener('submit', e => { e.preventDefault(); const offer = offers.find(o => o.id === $('application-offer').value); if (!offer) return; applications.push({id:offer.id,title:offer.title,date:$('application-date').value,status:$('application-status').value}); save(); renderApplications(); });
$('applications').addEventListener('change', e => { if (e.target.dataset.status !== undefined) { applications[Number(e.target.dataset.status)].status = e.target.value; save(); renderApplications(); }});
$('applications').addEventListener('click', e => { if (e.target.dataset.remove !== undefined) { applications.splice(Number(e.target.dataset.remove), 1); save(); renderApplications(); }});
$('export').addEventListener('click', () => { const blob = new Blob([JSON.stringify(applications, null, 2)], {type:'application/json'}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='mes_candidatures.json'; a.click(); URL.revokeObjectURL(url); });
$('check').addEventListener('click', () => { const late = applications.filter(a => a.status === 'Envoyée' && (Date.now() - new Date(`${a.date}T00:00:00`).getTime()) / 86400000 > 10); $('check-result').textContent = late.length ? `${late.length} candidature(s) sans réponse depuis plus de 10 jours : ${late.map(a => a.title).join(', ')}` : 'Aucune candidature sans réponse depuis plus de 10 jours.'; });
renderApplications();
fetch('data/matches.json').then(r => { if (!r.ok) throw Error(`HTTP ${r.status}`); return r.json(); }).then(renderData).catch(e => { $('notice').textContent = `Données indisponibles : ${e.message}. Exécutez le pipeline, puis ouvrez la page via un serveur HTTP.`; renderData({offers:[]}); });
