```dataviewjs

const folder = dv.current().file.folder;

// Lista de tarefas pendentes
dv.header(2, "Tarefas pendentes (todos os alvos)");
dv.taskList(
  dv.pages(`"${folder}"`)
    .file
    .path
    .map(path => dv.page(path))
    .filter(p => p.file.tasks && p.file.tasks.length > 0)
    .flatMap(p => p.file.tasks)
    .filter(t => !t.completed)
);
```
