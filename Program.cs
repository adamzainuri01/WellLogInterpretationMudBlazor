using Microsoft.AspNetCore.Mvc.ModelBinding;
using MudBlazor.Services;
using Well_Log_Mudblazor.Components;

var builder = WebApplication.CreateBuilder(args);

// Add MudBlazor services
builder.Services.AddMudServices();

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri("http://localhost:8000") });

builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogClass.LogValues>();
builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogClass.ResParams>();
builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogClass.PlotImage>();
builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogClass.PlotOptions>();
builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogClass.PlotData>();
builder.Services.AddScoped<Well_Log_Mudblazor.Models.LogTask.LogTask>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();
app.UseAntiforgery();

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
